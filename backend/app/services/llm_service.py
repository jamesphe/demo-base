from typing import Dict, Any, Optional, List, AsyncGenerator
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from datetime import datetime
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult, ChatGeneration, AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import Field, ConfigDict
import json
from openai import OpenAI  # 添加 OpenAI 导入
import logging
from pprint import pformat

# 条件导入智谱 AI SDK
try:
    import zhipuai
except ImportError:
    zhipuai = None

from app.models import LLMConfig
from app.core.config import settings
from .base import BaseService

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# 添加处理器到logger
if not logger.handlers:  # 避免重复添加处理器
    logger.addHandler(console_handler)

class ZhipuChatModel(BaseChatModel):
    """智谱 AI 聊天模型"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    api_key: str = Field(...)
    model_name: str = Field(default="GLM-4")
    temperature: float = Field(default=0.7)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        zhipuai.api_key = self.api_key
        
    @property
    def _llm_type(self) -> str:
        return "zhipu"

    async def _agenerate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        """异步生成回复"""
        try:
            # 转换消息格式
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            response = zhipuai.model_api.invoke(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature,
                **kwargs
            )
            
            if response.get('code') != 200:
                raise ValueError(f"智谱 API 调用失败: {response.get('msg')}")
            
            content = response['data']['choices'][0]['content']
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
            
        except Exception as e:
            raise ValueError(f"智谱 API 调用失败: {str(e)}")

    async def astream(self, messages: List[BaseMessage], **kwargs) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            response = zhipuai.model_api.sse_invoke(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature,
                incremental=True,
                **kwargs
            )
            
            for event in response.events():
                if event.event == "add":
                    yield event.data
                elif event.event in ["error", "interrupted"]:
                    raise ValueError(f"智谱 API 流式调用失败: {event.data}")
                    
        except Exception as e:
            raise ValueError(f"智谱 API 流式调用失败: {str(e)}")

class OllamaChatModel(BaseChatModel):
    """Ollama 聊天模型"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    api_url: str = Field(default="http://localhost:11434")
    model_name: str = Field(default="llama2")
    temperature: float = Field(default=0.7)
    
    async def _agenerate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        """异步生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": formatted_messages,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError(f"Ollama API调用失败: {response.text}")
                
                result = response.json()
                content = result["message"]["content"]
                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
                
        except Exception as e:
            raise ValueError(f"Ollama API调用失败: {str(e)}")

    async def astream(self, messages: List[BaseMessage], **kwargs) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": formatted_messages,
                        "stream": True,
                        "options": {
                            "temperature": self.temperature
                        }
                    }
                ) as response:
                    if response.status_code != 200:
                        raise ValueError(f"Ollama API调用失败: {response.status_code}")
                        
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data:
                                    yield data["message"]["content"]
                            except json.JSONDecodeError:
                                continue
                    
        except Exception as e:
            raise ValueError(f"Ollama API流式调用失败: {str(e)}")

class OpenAICompatibleChatModel(BaseChatModel):
    """OpenAI 兼容的聊天模型"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    api_url: str = Field(default="https://api.openai.com/v1")
    api_key: str = Field(...)
    model_name: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)
    client: Optional[OpenAI] = Field(default=None)  # 添加 client 字段
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )
        
    @property
    def _llm_type(self) -> str:
        return "openai_compatible"

    def _generate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        """同步生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature,
                **kwargs
            )
            
            message = AIMessage(content=completion.choices[0].message.content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
                
        except Exception as e:
            raise ValueError(f"OpenAI 兼容 API 调用失败: {str(e)}")

    async def _agenerate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        """异步生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature,
                stream=False,  # 确保不使用流式响应
                **kwargs
            )
            
            message = AIMessage(content=completion.choices[0].message.content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
                
        except Exception as e:
            raise ValueError(f"OpenAI 兼容 API 调用失败: {str(e)}")

    async def astream(self, messages: List[BaseMessage], **kwargs) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        try:
            formatted_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    formatted_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": message.content})
                else:
                    formatted_messages.append({"role": "user", "content": message.content})

            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=self.temperature,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise ValueError(f"OpenAI 兼容 API 流式调用失败: {str(e)}")

class LLMService(BaseService[LLMConfig, Any, Any]):
    """LLM 服务
    提供标准化的 LLM 调用接口，不处理具体业务逻辑
    """
    
    def __init__(self):
        super().__init__(LLMConfig)
        self._llm: Optional[BaseChatModel] = None
        logger.debug("LLMService initialized")

    async def get_default_config(self, db: Session) -> LLMConfig:
        """获取默认的 LLM 配置"""
        config = db.query(LLMConfig).filter(
            LLMConfig.is_default.is_(True),
            LLMConfig.is_enabled.is_(True)
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="未找到可用的默认 LLM 配置"
            )
            
        return config

    def _get_llm(self, config: LLMConfig) -> BaseChatModel:
        """获取 LLM 实例"""
        try:
            logger.debug("=== Getting LLM Instance ===")
            logger.debug(f"Provider: {config.provider}")
            logger.debug(f"Model: {config.chat_model}")
            logger.debug(f"Config: {pformat(config.__dict__)}")

            if not self._llm:
                if config.provider == "zhipu":
                    self._llm = ZhipuChatModel(
                        api_key=config.api_key,
                        model_name=config.chat_model,
                        temperature=config.chat_config.get("temperature", 0.7)
                    )
                elif config.provider == "ollama":
                    self._llm = OllamaChatModel(
                        api_url=config.api_url,
                        model_name=config.chat_model,
                        temperature=config.chat_config.get("temperature", 0.7)
                    )
                elif config.provider == "openai_compatible":
                    self._llm = OpenAICompatibleChatModel(
                        api_url=config.api_url,
                        api_key=config.api_key,
                        model_name=config.chat_model,
                        temperature=config.chat_config.get("temperature", 0.7)
                    )
                else:
                    logger.error(f"Unsupported provider: {config.provider}")
                    raise ValueError(f"不支持的 LLM 提供商: {config.provider}")
                
                logger.debug(f"Created new LLM instance: {type(self._llm).__name__}")
            else:
                logger.debug(f"Using cached LLM instance: {type(self._llm).__name__}")
            
            return self._llm
            
        except Exception as e:
            logger.error("Failed to get LLM instance", exc_info=True)
            logger.error(f"Error details: {str(e)}")
            raise

    async def generate_completion(
        self,
        prompt: str,
        llm_config: LLMConfig,
        system_prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """生成完成响应"""
        try:
            logger.debug("=== Generate Completion Start ===")
            logger.debug(f"Prompt: {prompt[:200]}...")  # 只显示前200个字符
            logger.debug(f"System Prompt: {system_prompt}")
            logger.debug(f"LLM Config: {pformat(llm_config.__dict__)}")
            logger.debug(f"Extra kwargs: {kwargs}")

            llm = self._get_llm(llm_config)
            logger.debug(f"LLM instance: {type(llm).__name__}")
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            logger.debug(f"Formatted messages: {pformat(messages)}")
            
            result = await llm._agenerate(messages, **kwargs)
            logger.debug(f"Raw result: {pformat(result.__dict__)}")
            
            response = {
                "content": result.generations[0].message.content
            }
            logger.debug(f"Final response: {pformat(response)}")
            return response
                
        except Exception as e:
            logger.error("Generate completion failed", exc_info=True)
            logger.error(f"Error details: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"LLM 调用失败: {str(e)}"
            )

    async def stream_completion(
        self,
        prompt: str,
        llm_config: LLMConfig,
        system_prompt: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成完成响应"""
        try:
            logger.debug("=== Stream Completion Start ===")
            logger.debug(f"Prompt: {prompt[:200]}...")
            logger.debug(f"System Prompt: {system_prompt}")
            logger.debug(f"LLM Config: {pformat(llm_config.__dict__)}")
            logger.debug(f"Extra kwargs: {kwargs}")

            llm = self._get_llm(llm_config)
            logger.debug(f"LLM instance: {type(llm).__name__}")
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            logger.debug(f"Formatted messages: {pformat(messages)}")
            
            chunk_count = 0
            async for chunk in llm.astream(messages, **kwargs):
                chunk_count += 1
                if chunk_count % 10 == 0:  # 每10个chunk记录一次
                    logger.debug(f"Streaming chunk #{chunk_count}: {chunk[:50]}...")
                yield chunk
            
            logger.debug(f"Total chunks streamed: {chunk_count}")
                
        except Exception as e:
            logger.error("Stream completion failed", exc_info=True)
            logger.error(f"Error details: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"LLM 流式调用失败: {str(e)}"
            )

# 创建服务实例
llm_service = LLMService()

# 只导出实例
__all__ = ["llm_service"] 
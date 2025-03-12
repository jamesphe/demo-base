from typing import Optional, Dict, Any
import httpx
from app.core.config import settings


async def validate_llm_connection(
    provider: str,
    api_url: Optional[str],
    api_key: Optional[str],
    model_config: Optional[Dict[str, Any]] = None
) -> bool:
    """验证 LLM 服务连接是否正常
    
    Args:
        provider: LLM 提供商 (zhipu, qianwen, ollama, openai)
        api_url: API 地址
        api_key: API 密钥
        model_config: 模型配置
        
    Returns:
        bool: 连接是否正常
    """
    try:
        if provider == "zhipu":
            return await _validate_zhipu(api_key)
        elif provider == "qianwen":
            return await _validate_qianwen(api_key)
        elif provider == "ollama":
            return await _validate_ollama(api_url or "http://localhost:11434")
        elif provider == "openai":
            return await _validate_openai(api_key, api_url)
        else:
            return False
    except Exception as e:
        print(f"LLM connection validation error: {str(e)}")
        return False


async def _validate_zhipu(api_key: str) -> bool:
    """验证智谱 AI 连接"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://open.bigmodel.cn/api/paas/v3/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.status_code == 200
    except Exception:
        return False


async def _validate_qianwen(api_key: str) -> bool:
    """验证阿里千问连接"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.status_code == 200
    except Exception:
        return False


async def _validate_ollama(api_url: str) -> bool:
    """验证 Ollama 连接"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_url}/api/tags")
            return response.status_code == 200
    except Exception:
        return False


async def _validate_openai(api_key: str, api_url: Optional[str] = None) -> bool:
    """验证 OpenAI 连接"""
    try:
        url = api_url or "https://api.openai.com/v1/models"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.status_code == 200
    except Exception:
        return False 
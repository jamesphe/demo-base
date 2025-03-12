from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from app.db.base_class import Base
from datetime import datetime


class LLMConfig(Base):
    """Model for storing LLM configurations.
    
    支持的提供商:
    - zhipu: 智谱AI
    - qianwen: 阿里千问
    - ollama: Ollama本地模型
    - openai: OpenAI及兼容接口(如Azure、Claude等)
    """
    
    __tablename__ = "llm_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider = Column(String)  # ollama, zhipu, openai
    api_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    
    # 对话模型配置
    chat_model = Column(String)  # 对话模型名称
    chat_config = Column(JSON, nullable=True)  # 对话模型配置
    
    # 向量化模型配置
    embedding_model = Column(String, nullable=True)  # 向量化模型名称
    embedding_config = Column(JSON, nullable=True)  # 向量化模型配置
    
    is_default = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    ) 
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class LLMConfigBase(BaseModel):
    name: str
    provider: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    chat_model: str
    chat_config: Optional[Dict] = None
    embedding_model: Optional[str] = None
    embedding_config: Optional[Dict] = None
    is_default: bool = False
    is_enabled: bool = True


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(LLMConfigBase):
    name: Optional[str] = None
    provider: Optional[str] = None
    chat_model: Optional[str] = None


class LLMConfigInDBBase(LLMConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LLMConfig(LLMConfigInDBBase):
    pass 
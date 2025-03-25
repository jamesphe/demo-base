from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ResumeRepositoryBase(BaseModel):
    """简历库基础模型"""
    name: str
    resume_type: str
    description: Optional[str] = None
    tenant_id: Optional[int] = None


class ResumeRepositoryCreate(ResumeRepositoryBase):
    """创建简历库模型"""
    pass


class ResumeRepositoryUpdate(ResumeRepositoryBase):
    """更新简历库模型"""
    pass


class ResumeRepository(ResumeRepositoryBase):
    """简历库返回模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
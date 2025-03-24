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
    name: Optional[str] = None
    resume_type: Optional[str] = None
    processing_status: Optional[str] = None
    processing_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None


class ResumeRepository(ResumeRepositoryBase):
    """简历库返回模型"""
    id: int
    processing_status: str
    processing_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
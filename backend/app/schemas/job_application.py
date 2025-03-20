from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobApplicationBase(BaseModel):
    """职位申请基础模型"""
    resume_id: int = Field(..., description="简历ID")


class JobApplicationCreate(JobApplicationBase):
    """创建职位申请"""
    pass


class JobApplicationUpdate(BaseModel):
    """更新职位申请状态"""
    status: str = Field(..., description="申请状态")
    review_notes: Optional[str] = Field(None, description="审核备注")


class JobApplication(JobApplicationBase):
    """职位申请完整模型"""
    application_id: int
    job_id: int
    status: str
    apply_time: datetime
    review_time: Optional[datetime]
    review_notes: Optional[str]

    class Config:
        from_attributes = True 
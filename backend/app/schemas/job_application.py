from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobApplicationBase(BaseModel):
    """职位申请基础模型"""
    job_id: int
    resume_id: int
    status: str = "pending"  # pending, approved, rejected, withdrawn
    tenant_id: Optional[int] = None
    created_by: Optional[int] = None


class JobApplicationCreate(JobApplicationBase):
    """创建职位申请"""
    pass


class JobApplicationUpdate(BaseModel):
    """更新职位申请状态"""
    status: Optional[str] = None
    interview_feedback: Optional[str] = None
    rejection_reason: Optional[str] = None
    updated_by: Optional[int] = None


class JobApplicationInDBBase(JobApplicationBase):
    """数据库中的职位申请模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobApplication(JobApplicationInDBBase):
    """API返回的职位申请模型"""
    pass


class JobApplicationWithDetails(JobApplication):
    """带有详细信息的职位申请模型"""
    job_title: Optional[str] = None
    candidate_name: Optional[str] = None
    resume_name: Optional[str] = None 
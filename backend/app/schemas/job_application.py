from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.resume import Resume, ResumeBase


class JobApplicationBase(BaseModel):
    """职位申请基础模型"""
    job_id: int
    resume_id: int
    status: Optional[str] = "pending"  # pending, approved, rejected, withdrawn
    tenant_id: Optional[int] = None
    created_by: Optional[int] = None
    review_notes: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    """创建职位申请"""
    pass


class JobApplicationUpdate(BaseModel):
    """更新职位申请状态"""
    status: Optional[str] = None
    interview_feedback: Optional[str] = None
    rejection_reason: Optional[str] = None
    updated_by: Optional[int] = None
    review_notes: Optional[str] = None
    match_score: Optional[float] = None
    match_reason: Optional[str] = None


class JobApplicationInDBBase(JobApplicationBase):
    """数据库中的职位申请模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    apply_time: datetime
    review_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobApplication(JobApplicationInDBBase):
    """API返回的职位申请模型"""
    match_score: Optional[float] = None
    match_reason: Optional[str] = None


class JobApplicationWithDetails(JobApplication):
    """带有详细信息的职位申请模型"""
    job_title: Optional[str] = None
    candidate_name: Optional[str] = None
    resume_name: Optional[str] = None


class JobApplicationWithResume(JobApplication):
    """增强的职位申请响应模型，包含简历信息"""
    resume: Resume

    class Config:
        from_attributes = True


class ResumeInfo(BaseModel):
    """简历基本信息"""
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None

    class Config:
        from_attributes = True


class JobInfo(BaseModel):
    """职位基本信息"""
    id: int
    title: str
    department_name: Optional[str] = None
    publisher_name: str

    class Config:
        from_attributes = True


class JobApplicationWithResumeInfo(JobApplicationBase):
    """增强的职位申请响应模型，包含简历基本信息"""
    id: int
    created_at: datetime
    updated_at: datetime
    apply_time: datetime
    resume_name: str
    candidate_name: str
    resume_phone: Optional[str] = None
    resume_email: Optional[str] = None
    resume_highest_education: Optional[str] = None
    resume_experience_years: Optional[int] = None
    match_score: Optional[float] = None
    match_reason: Optional[str] = None
    resume: ResumeInfo
    job: JobInfo
    tenant_name: str

    class Config:
        from_attributes = True


class JobApplicationListMeta(BaseModel):
    """职位申请列表元数据"""
    total: int
    page: int
    per_page: int
    total_pages: int


class JobApplicationListResponse(BaseModel):
    """职位申请列表响应"""
    data: List[JobApplicationWithResumeInfo]
    meta: JobApplicationListMeta 
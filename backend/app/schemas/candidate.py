from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .interview import Interview
from .common import ListResponse


class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    status: Optional[str] = None
    tenant_id: Optional[int] = None
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(CandidateBase):
    pass


class Candidate(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 添加带有面试信息的 Candidate Schema
class CandidateWithInterviews(Candidate):
    interviews: List[Interview] = []

    class Config:
        from_attributes = True


class CandidateListResponse(ListResponse[CandidateWithInterviews]):
    """候选人列表响应模型"""
    pass 
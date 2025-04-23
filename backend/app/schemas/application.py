from typing import List, Optional
from pydantic import BaseModel


class ApplicationBatchUpdateRequest(BaseModel):
    """批量更新职位申请状态请求"""
    ids: List[int]
    status: str
    reviewNotes: Optional[str] = None


class ApplicationInfo(BaseModel):
    """申请信息"""
    id: int
    resume_id: int
    job_id: int
    tenant_id: int
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None


class ConvertToCandidatesRequest(BaseModel):
    """将申请转为候选人请求"""
    applications: List[ApplicationInfo]
    status: str
    notes: Optional[str] = None
    tenant_id: Optional[int] = None 
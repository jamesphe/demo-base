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
    email: str
    candidate_name: Optional[str] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    job_id: int
    tenant_id: int
    resume_id: Optional[int] = None 
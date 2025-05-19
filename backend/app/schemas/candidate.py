from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .common import ListResponse

# 注意: 这个模块已经废弃，但为了兼容性暂时保留
# 请不要在新代码中使用Candidate相关的模型

class CandidateBase(BaseModel):
    """
    已废弃: 候选人基础模型
    请使用Talent或其他模型代替
    """
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    tenant_id: Optional[int] = None
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """已废弃: 创建候选人模型"""
    pass


class CandidateUpdate(CandidateBase):
    """已废弃: 更新候选人模型"""
    pass


class Candidate(CandidateBase):
    """已废弃: 候选人模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # 添加职位名称和简历名称字段
    job_title: Optional[str] = None
    resume_name: Optional[str] = None

    class Config:
        from_attributes = True


# 简化版的候选人模型，仅用于兼容现有API
class CandidateWithInterviews(Candidate):
    """已废弃: 带面试信息的候选人模型"""
    interviews: List[dict] = []

    class Config:
        from_attributes = True


class CandidateListResponse(ListResponse[Candidate]):
    """已废弃: 候选人列表响应模型"""
    pass


class CandidateBatchUpdate(BaseModel):
    """已废弃: 批量更新候选人状态的请求模型"""
    candidate_ids: List[int]
    status: int 
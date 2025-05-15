from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
from enum import Enum
from .common import ListResponse


class InterviewType(str, Enum):
    """面试类型"""
    FIRST = "first"  # 初试
    SECOND = "second"  # 复试
    FINAL = "final"  # 终试


class InterviewBase(BaseModel):
    resume_id: int
    job_id: int
    status: Optional[str] = "待安排"  # 待安排、已安排、已完成、已取消
    schedule_time: Optional[datetime] = None
    feedback: Optional[str] = None
    location: Optional[str] = None  # 面试地点
    # 面试类型：初试、复试、终试
    interview_type: Optional[InterviewType] = InterviewType.FIRST
    duration: Optional[int] = 60  # 面试时长(分钟)
    notes: Optional[str] = None  # 面试备注


class InterviewCreate(InterviewBase):
    candidate_id: Optional[int] = None  # 候选人ID，用于验证
    interviewer_ids: Optional[List[int]] = None  # 面试官ID列表
    type: Optional[str] = None  # 接收前端的type字段
    time: Optional[str] = None  # 接收前端的time字段
    candidates: Optional[List[dict]] = None  # 接收前端的candidates数组


class InterviewUpdate(InterviewBase):
    interviewer_ids: Optional[List[int]] = None  # 面试官ID列表


class Interview(InterviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 添加带有详细信息的面试 Schema
class InterviewWithDetails(Interview):
    resume_title: Optional[str] = None
    job_title: Optional[str] = None
    interviewer_names: Optional[List[str]] = None  # 面试官名字列表
    
    # ORM对象，所以不使用Dict类型
    resume: Optional[Any] = None
    interviewers: Optional[List[Any]] = None  # 面试官列表
    job: Optional[Any] = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class InterviewListResponse(ListResponse[InterviewWithDetails]):
    """面试列表响应模型"""
    pass


class FocusPoints(BaseModel):
    content: str  # 统一存储所有面试关注点内容
    technical: Optional[str] = None  # 保留向后兼容
    project: Optional[str] = None    # 保留向后兼容
    comprehensive: Optional[str] = None  # 保留向后兼容


class InterviewGuideRequest(BaseModel):
    resumeId: int
    jobId: int
    role: str
    focusPoints: FocusPoints 
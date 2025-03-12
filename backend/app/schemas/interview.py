from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator


class InterviewBase(BaseModel):
    candidate_id: int
    interviewer_id: Optional[int] = None
    status: Optional[str] = "待安排"  # 待安排、已安排、已完成、已取消
    schedule_time: Optional[datetime] = None
    feedback: Optional[str] = None


class InterviewCreate(InterviewBase):
    pass


class InterviewUpdate(InterviewBase):
    pass


class Interview(InterviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 添加带有详细信息的面试 Schema
class InterviewWithDetails(Interview):
    candidate_name: Optional[str] = None
    interviewer_name: Optional[str] = None
    job_title: Optional[str] = None

    class Config:
        from_attributes = True 
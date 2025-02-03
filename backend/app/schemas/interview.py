from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InterviewBase(BaseModel):
    candidate_id: Optional[int] = None
    interviewer_id: Optional[int] = None
    status: Optional[str] = None
    schedule_time: Optional[datetime] = None
    feedback: Optional[str] = None


class InterviewCreate(InterviewBase):
    candidate_id: int
    interviewer_id: int
    schedule_time: datetime


class InterviewUpdate(InterviewBase):
    pass


class InterviewInDBBase(InterviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Interview(InterviewInDBBase):
    pass 
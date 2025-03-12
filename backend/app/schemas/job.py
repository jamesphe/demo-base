from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = True
    tenant_id: Optional[int] = None


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    pass


class Job(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 添加带有候选人数量的 Job Schema
class JobWithCandidateCount(Job):
    candidate_count: int

    class Config:
        from_attributes = True 
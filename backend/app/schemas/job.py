from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class JobBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = True


class JobCreate(JobBase):
    title: str
    description: str


class JobUpdate(JobBase):
    pass


class JobInDBBase(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Job(JobInDBBase):
    pass 
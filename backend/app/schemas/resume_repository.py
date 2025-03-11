from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ResumeRepositoryBase(BaseModel):
    name: str
    resume_type: str = "general"
    description: Optional[str] = None


class ResumeRepositoryCreate(ResumeRepositoryBase):
    pass


class ResumeRepositoryUpdate(ResumeRepositoryBase):
    processing_status: Optional[str] = None
    processing_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None


class ResumeRepository(ResumeRepositoryBase):
    id: int
    processing_status: str
    processing_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    } 
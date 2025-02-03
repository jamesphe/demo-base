from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class CandidateBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    status: Optional[str] = None


class CandidateCreate(CandidateBase):
    name: str
    email: EmailStr


class CandidateUpdate(CandidateBase):
    pass


class CandidateInDBBase(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Candidate(CandidateInDBBase):
    pass 
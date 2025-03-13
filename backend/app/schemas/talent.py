from pydantic import BaseModel
from datetime import date
from typing import Optional


class TalentBase(BaseModel):
    name: str
    gender: Optional[str]
    birth_date: Optional[date]
    phone: str
    email: Optional[str]
    address: Optional[str]
    profile_summary: Optional[str]
    primary_job_type: Optional[str]
    job_location_preference: Optional[str]
    expected_salary: Optional[str]


class TalentCreate(TalentBase):
    tenant_id: Optional[int]


class TalentUpdate(TalentBase):
    pass


class TalentResponse(TalentBase):
    talent_id: int
    verified_status: bool
    
    class Config:
        from_attributes = True 
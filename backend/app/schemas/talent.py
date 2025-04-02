from pydantic import BaseModel
from datetime import date
from typing import Optional
from .common import ListResponse


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
    id: int
    verified_status: bool
    
    class Config:
        from_attributes = True 


class TalentListResponse(ListResponse[TalentResponse]):
    """人才列表响应模型"""
    pass 
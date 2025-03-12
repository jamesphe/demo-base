from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TalentPoolBase(BaseModel):
    pool_name: str
    description: Optional[str]


class TalentPoolCreate(TalentPoolBase):
    tenant_id: int


class TalentPoolUpdate(TalentPoolBase):
    pass


class TalentPoolResponse(TalentPoolBase):
    pool_id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TalentPoolMemberBase(BaseModel):
    talent_id: int
    remark: Optional[str]


class TalentPoolMemberCreate(TalentPoolMemberBase):
    pool_id: int


class TalentPoolMemberUpdate(TalentPoolMemberBase):
    pass


class TalentPoolMemberResponse(TalentPoolMemberBase):
    member_id: int
    pool_id: int
    added_at: datetime

    class Config:
        orm_mode = True 
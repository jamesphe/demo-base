from pydantic import BaseModel
from typing import Optional
from datetime import date


class TalentEducationBase(BaseModel):
    institution_name: str
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[date]
    graduation_date: Optional[date]
    certificate_url: Optional[str]
    description: Optional[str]


class TalentEducationCreate(TalentEducationBase):
    talent_id: int


class TalentEducationUpdate(TalentEducationBase):
    pass


class TalentEducationResponse(TalentEducationBase):
    education_id: int
    talent_id: int

    class Config:
        from_attributes = True 
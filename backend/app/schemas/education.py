from pydantic import BaseModel
from typing import Optional
from datetime import date


class EducationBase(BaseModel):
    institution_name: str
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[date]
    graduation_date: Optional[date]
    certificate_url: Optional[str]
    description: Optional[str]


class EducationCreate(EducationBase):
    talent_id: int


class EducationUpdate(EducationBase):
    pass


class EducationResponse(EducationBase):
    education_id: int
    talent_id: int

    class Config:
        orm_mode = True 
from pydantic import BaseModel
from typing import Optional
from datetime import date


class ExperienceBase(BaseModel):
    company_name: str
    position: str
    start_date: date
    end_date: Optional[date]
    job_description: Optional[str]
    achievements: Optional[str]
    attachment_url: Optional[str]


class ExperienceCreate(ExperienceBase):
    talent_id: int


class ExperienceUpdate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    experience_id: int
    talent_id: int

    class Config:
        orm_mode = True 
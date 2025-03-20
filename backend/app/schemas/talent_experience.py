from pydantic import BaseModel
from typing import Optional
from datetime import date


class TalentExperienceBase(BaseModel):
    company_name: str
    position: str
    start_date: date
    end_date: Optional[date]
    job_description: Optional[str]
    achievements: Optional[str]
    attachment_url: Optional[str]


class TalentExperienceCreate(TalentExperienceBase):
    talent_id: int


class TalentExperienceUpdate(TalentExperienceBase):
    pass


class TalentExperienceResponse(TalentExperienceBase):
    experience_id: int
    talent_id: int

    class Config:
        from_attributes = True 
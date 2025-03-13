from pydantic import BaseModel
from typing import Optional


class SkillBase(BaseModel):
    skill_name: str
    skill_description: Optional[str]
    category: Optional[str]


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    pass


class SkillResponse(SkillBase):
    skill_id: int
    
    class Config:
        from_attributes = True 
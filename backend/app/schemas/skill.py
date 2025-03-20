from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tenant_id: Optional[int] = None  # None表示平台公共技能
    status: Optional[str] = 'active'


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    pass


class Skill(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 
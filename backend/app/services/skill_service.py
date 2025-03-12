from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate


class SkillService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_skill(self, skill: SkillCreate) -> Skill:
        """创建技能"""
        db_skill = Skill(
            skill_name=skill.skill_name,
            skill_description=skill.skill_description,
            category=skill.category
        )
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill
    
    def get_skill(self, skill_id: int) -> Optional[Skill]:
        """获取单个技能"""
        return self.db.query(Skill).filter(Skill.skill_id == skill_id).first()
    
    def list_skills(self, skip: int = 0, limit: int = 100) -> List[Skill]:
        """获取技能列表"""
        return self.db.query(Skill).offset(skip).limit(limit).all()
    
    def update_skill(
        self, 
        skill_id: int, 
        skill_update: SkillUpdate
    ) -> Optional[Skill]:
        """更新技能信息"""
        db_skill = self.get_skill(skill_id)
        if not db_skill:
            return None
            
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_skill, field, value)
            
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill 
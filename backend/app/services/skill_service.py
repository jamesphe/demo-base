from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate


class SkillService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_skill(self, skill: SkillCreate, tenant_id: Optional[int] = None) -> Skill:
        """创建技能"""
        db_skill = Skill(
            tenant_id=tenant_id or skill.tenant_id,  # 优先使用传入的tenant_id
            skill_name=skill.skill_name,
            skill_description=skill.skill_description,
            category=skill.category,
            status=skill.status
        )
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill
    
    def get_skill(self, skill_id: int) -> Optional[Skill]:
        """获取单个技能"""
        return self.db.query(Skill).filter(Skill.skill_id == skill_id).first()
    
    def list_skills(
        self, 
        skip: int = 0, 
        limit: int = 100,
        tenant_id: Optional[int] = None
    ) -> List[Skill]:
        """获取技能列表
        
        Args:
            tenant_id: 如果指定,则只返回该租户的技能和公共技能
        """
        query = self.db.query(Skill)
        if tenant_id is not None:
            # 返回指定租户的技能和公共技能
            query = query.filter(
                (Skill.tenant_id == tenant_id) | (Skill.tenant_id.is_(None))
            )
        return query.offset(skip).limit(limit).all()
    
    def update_skill(
        self, 
        skill_id: int, 
        skill_update: SkillUpdate,
        tenant_id: Optional[int] = None
    ) -> Optional[Skill]:
        """更新技能信息"""
        query = self.db.query(Skill).filter(Skill.skill_id == skill_id)
        
        # 如果指定了tenant_id,则只能更新该租户的技能
        if tenant_id is not None:
            query = query.filter(Skill.tenant_id == tenant_id)
            
        db_skill = query.first()
        if not db_skill:
            return None
            
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_skill, field, value)
            
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill 
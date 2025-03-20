from typing import List, Optional
from sqlalchemy.orm import Session
from app import models
from app.schemas.skill import SkillCreate, SkillUpdate
from .base import BaseService


class SkillService(BaseService[models.Skill, SkillCreate, SkillUpdate]):
    """技能服务"""
    
    def __init__(self):
        super().__init__(models.Skill)

    def create_skill(
        self,
        db: Session,
        skill: SkillCreate,
        tenant_id: int = None
    ) -> models.Skill:
        """创建技能"""
        db_skill = models.Skill(
            name=skill.name,
            description=skill.description,
            category=skill.category,
            tenant_id=tenant_id,
            status=skill.status
        )
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)
        return db_skill
    
    def get_skill(
        self,
        db: Session,
        skill_id: int
    ) -> Optional[models.Skill]:
        """获取单个技能"""
        return db.query(models.Skill).filter(
            models.Skill.id == skill_id
        ).first()
    
    def list_skills(
        self,
        db: Session,
        skip: int = 0, 
        limit: int = 100,
        tenant_id: Optional[int] = None
    ) -> List[models.Skill]:
        """获取技能列表"""
        query = db.query(models.Skill)
        if tenant_id is not None:
            query = query.filter(
                (models.Skill.tenant_id == tenant_id) | 
                (models.Skill.tenant_id.is_(None))
            )
        return query.offset(skip).limit(limit).all()
    
    def update_skill(
        self,
        db: Session,
        skill_id: int, 
        skill_update: SkillUpdate,
        tenant_id: Optional[int] = None
    ) -> Optional[models.Skill]:
        """更新技能信息"""
        query = db.query(models.Skill).filter(models.Skill.id == skill_id)
        
        if tenant_id is not None:
            query = query.filter(models.Skill.tenant_id == tenant_id)
            
        db_skill = query.first()
        if not db_skill:
            return None
            
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_skill, field, value)
            
        db.commit()
        db.refresh(db_skill)
        return db_skill


# 创建服务实例
skill_service = SkillService()

# 只导出实例
__all__ = ["skill_service"] 
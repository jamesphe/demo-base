from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.talent_experience import TalentExperience
from app.schemas.talent_experience import TalentExperienceCreate, TalentExperienceUpdate


class ExperienceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_experience(
        self,
        experience: TalentExperienceCreate
    ) -> TalentExperience:
        """创建工作经验"""
        db_experience = TalentExperience(
            talent_id=experience.talent_id,
            company_name=experience.company_name,
            position=experience.position,
            start_date=experience.start_date,
            end_date=experience.end_date,
            job_description=experience.job_description,
            achievements=experience.achievements,
            attachment_url=experience.attachment_url
        )
        self.db.add(db_experience)
        self.db.commit()
        self.db.refresh(db_experience)
        return db_experience
    
    def get_experience(
        self,
        experience_id: int
    ) -> Optional[TalentExperience]:
        """获取单个工作经验"""
        return (self.db.query(TalentExperience)
                .filter(TalentExperience.experience_id == experience_id)
                .first())
    
    def list_talent_experiences(
        self,
        talent_id: int
    ) -> List[TalentExperience]:
        """获取人才的所有工作经验"""
        return (self.db.query(TalentExperience)
                .filter(TalentExperience.talent_id == talent_id)
                .all())
    
    def update_experience(
        self,
        experience_id: int,
        experience: TalentExperienceUpdate
    ) -> Optional[TalentExperience]:
        """更新工作经验"""
        db_experience = self.get_experience(experience_id)
        if not db_experience:
            return None
            
        update_data = experience.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_experience, field, value)
            
        self.db.commit()
        self.db.refresh(db_experience)
        return db_experience
    
    def delete_experience(self, experience_id: int) -> bool:
        """删除工作经验"""
        db_experience = self.get_experience(experience_id)
        if not db_experience:
            return False
            
        self.db.delete(db_experience)
        self.db.commit()
        return True 
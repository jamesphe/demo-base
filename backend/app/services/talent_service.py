from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.talent import Talent
from app.schemas.talent import TalentCreate, TalentUpdate
from datetime import datetime


class TalentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_talent(self, talent: TalentCreate) -> Talent:
        """创建人才记录"""
        db_talent = Talent(
            tenant_id=talent.tenant_id,
            name=talent.name,
            gender=talent.gender,
            birth_date=talent.birth_date,
            phone=talent.phone,
            email=talent.email,
            address=talent.address,
            profile_summary=talent.profile_summary,
            primary_job_type=talent.primary_job_type,
            job_location_preference=talent.job_location_preference,
            expected_salary=talent.expected_salary,
            registration_date=datetime.utcnow(),
            verified_status=False
        )
        self.db.add(db_talent)
        self.db.commit()
        self.db.refresh(db_talent)
        return db_talent
    
    def get_talent(self, talent_id: int) -> Optional[Talent]:
        """获取单个人才信息"""
        return (self.db.query(Talent)
                .filter(Talent.talent_id == talent_id)
                .first())
    
    def update_talent(
        self, 
        talent_id: int, 
        talent_update: TalentUpdate
    ) -> Optional[Talent]:
        """更新人才信息"""
        db_talent = self.get_talent(talent_id)
        if not db_talent:
            return None
            
        update_data = talent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_talent, field, value)
            
        self.db.commit()
        self.db.refresh(db_talent)
        return db_talent
    
    def list_talents(self, skip: int = 0, limit: int = 100) -> List[Talent]:
        """获取人才列表"""
        return self.db.query(Talent).offset(skip).limit(limit).all()
        
    def delete_talent(self, talent_id: int) -> bool:
        """删除人才信息"""
        db_talent = self.get_talent(talent_id)
        if not db_talent:
            return False
            
        self.db.delete(db_talent)
        self.db.commit()
        return True 
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.trial_application import TrialApplication
from app.schemas.trial_application import TrialApplicationCreate, TrialApplicationUpdate


class CRUDTrialApplication(CRUDBase[TrialApplication, TrialApplicationCreate, TrialApplicationUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[TrialApplication]:
        """获取用户最新的试用申请"""
        return db.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).first()
    
    def create_with_user(
        self, db: Session, *, obj_in: TrialApplicationCreate, user_id: int
    ) -> TrialApplication:
        """创建试用申请"""
        obj_in_data = obj_in.dict() if isinstance(obj_in, TrialApplicationCreate) else obj_in
        
        db_obj = TrialApplication(
            user_id=user_id,
            status="pending",
            created_at=datetime.now(),
            company_name=obj_in_data.get("company_name"),
            contact_name=obj_in_data.get("contact_name"),
            contact_phone=obj_in_data.get("contact_phone"),
            contact_email=obj_in_data.get("contact_email"),
            company_size=obj_in_data.get("company_size"),
            business_description=obj_in_data.get("business_description"),
            application_reason=obj_in_data.get("application_reason")
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_pending_applications(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TrialApplication]:
        """获取待审核的试用申请"""
        return db.query(self.model).filter(
            self.model.status == "pending"
        ).offset(skip).limit(limit).all()

    def get_by_email(self, db: Session, *, email: str) -> Optional[TrialApplication]:
        """根据邮箱地址获取试用申请记录"""
        return db.query(self.model).filter(
            self.model.contact_email == email
        ).first()


trial_application = CRUDTrialApplication(TrialApplication) 
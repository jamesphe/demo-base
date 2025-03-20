from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.job_application import JobApplication
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate
)


class CRUDJobApplication(
    CRUDBase[JobApplication, JobApplicationCreate, JobApplicationUpdate]
):
    def get_by_job(
        self, db: Session, *, job_id: int
    ) -> List[JobApplication]:
        """获取指定职位的所有申请"""
        return db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()

    def get_by_resume(
        self, db: Session, *, resume_id: int
    ) -> List[JobApplication]:
        """获取指定简历的所有申请"""
        return db.query(self.model).filter(
            self.model.resume_id == resume_id
        ).all()

    def get_by_job_and_resume(
        self, db: Session, *, job_id: int, resume_id: int
    ) -> Optional[JobApplication]:
        """检查是否已经申请过该职位"""
        return db.query(self.model).filter(
            self.model.job_id == job_id,
            self.model.resume_id == resume_id
        ).first()

    def get_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定租户的所有职位申请"""
        return db.query(self.model).filter(
            self.model.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定状态的所有职位申请"""
        return db.query(self.model).filter(
            self.model.status == status
        ).offset(skip).limit(limit).all()

    def update_status(
        self,
        db: Session,
        *,
        application_id: int,
        status: str,
        review_notes: Optional[str] = None
    ) -> JobApplication:
        """更新职位申请状态"""
        application = self.get(db, id=application_id)
        if not application:
            return None
        
        update_data = {
            "status": status,
            "review_time": datetime.utcnow(),
            "review_notes": review_notes
        }
        return super().update(db, db_obj=application, obj_in=update_data)

    def create_with_owner(
        self, 
        db: Session, 
        *, 
        obj_in: JobApplicationCreate, 
        tenant_id: int,
        created_by: int
    ) -> JobApplication:
        """创建职位申请"""
        db_obj = JobApplication(
            job_id=obj_in.job_id,
            resume_id=obj_in.resume_id,
            status=obj_in.status if obj_in.status else "pending",
            tenant_id=tenant_id,
            created_by=created_by,
            apply_time=datetime.utcnow(),
            review_notes=obj_in.review_notes if hasattr(obj_in, "review_notes") else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定租户的所有职位申请"""
        return self.get_by_tenant(db=db, tenant_id=tenant_id, skip=skip, limit=limit)


job_application = CRUDJobApplication(JobApplication) 
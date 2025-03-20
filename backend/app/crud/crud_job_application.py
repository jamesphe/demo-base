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
        return db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()

    def get_by_resume(
        self, db: Session, *, resume_id: int
    ) -> List[JobApplication]:
        return db.query(self.model).filter(
            self.model.resume_id == resume_id
        ).all()

    def update_status(
        self,
        db: Session,
        *,
        application_id: int,
        status: str,
        review_notes: Optional[str] = None
    ) -> JobApplication:
        application = self.get(db, id=application_id)
        if not application:
            return None
        
        update_data = {
            "status": status,
            "review_time": datetime.utcnow(),
            "review_notes": review_notes
        }
        return super().update(db, db_obj=application, obj_in=update_data)


job_application = CRUDJobApplication(JobApplication) 
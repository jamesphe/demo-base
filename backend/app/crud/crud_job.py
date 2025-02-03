from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class CRUDJob(CRUDBase[Job, JobCreate, JobUpdate]):
    def get_by_title(self, db: Session, *, title: str) -> Optional[Job]:
        return db.query(Job).filter(Job.title == title).first()

    def get_active(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        return db.query(Job).filter(Job.is_active == True).offset(skip).limit(limit).all()


job = CRUDJob(Job) 
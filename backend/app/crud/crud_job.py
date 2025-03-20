from typing import List, Optional, Union, Dict, Any
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

    def get_by_external_id(self, db: Session, *, external_id: str) -> Optional[Job]:
        return db.query(Job).filter(Job.external_id == external_id).first()

    def update_by_external_id(
        self, db: Session, *, external_id: str, obj_in: Union[JobUpdate, Dict[str, Any]]
    ) -> Optional[Job]:
        db_obj = self.get_by_external_id(db, external_id=external_id)
        if not db_obj:
            return None
        return self.update(db, db_obj=db_obj, obj_in=obj_in)

    def remove_by_external_id(self, db: Session, *, external_id: str) -> Optional[Job]:
        obj = self.get_by_external_id(db, external_id=external_id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj


job = CRUDJob(Job) 
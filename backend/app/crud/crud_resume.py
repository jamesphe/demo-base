from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate


class CRUDResume(CRUDBase[Resume, ResumeCreate, ResumeUpdate]):
    def get_by_resume_id(self, db: Session, *, resume_id: str) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.resume_id == resume_id).first()

    def get_by_repository(
        self,
        db: Session,
        *,
        repository_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.repository_id == repository_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.processing_status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_candidate(
        self,
        db: Session,
        *,
        candidate_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        return (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


resume = CRUDResume(Resume) 
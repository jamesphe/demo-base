from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.resume_repository import ResumeRepository
from app.schemas.resume_repository import ResumeRepositoryCreate, ResumeRepositoryUpdate


class CRUDRepository(CRUDBase[ResumeRepository, ResumeRepositoryCreate, ResumeRepositoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ResumeRepository]:
        return db.query(ResumeRepository).filter(ResumeRepository.name == name).first()

    def get_by_type(
        self, db: Session, *, resume_type: str, skip: int = 0, limit: int = 100
    ) -> List[ResumeRepository]:
        return (
            db.query(ResumeRepository)
            .filter(ResumeRepository.resume_type == resume_type)
            .offset(skip)
            .limit(limit)
            .all()
        )


repository = CRUDRepository(ResumeRepository) 
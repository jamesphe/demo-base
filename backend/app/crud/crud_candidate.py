from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CRUDCandidate(CRUDBase[Candidate, CandidateCreate, CandidateUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.email == email).first()

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Candidate]:
        return (
            db.query(Candidate)
            .filter(Candidate.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )


candidate = CRUDCandidate(Candidate) 
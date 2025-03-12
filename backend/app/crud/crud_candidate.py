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
        
    def get_multi_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        """获取指定租户的候选人列表"""
        return (
            db.query(Candidate)
            .filter(Candidate.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_tenant(
        self,
        db: Session,
        *,
        obj_in: CandidateCreate,
        tenant_id: int
    ) -> Candidate:
        """创建带有租户ID的候选人"""
        obj_in_data = obj_in.dict()
        db_obj = Candidate(**obj_in_data, tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


candidate = CRUDCandidate(Candidate) 
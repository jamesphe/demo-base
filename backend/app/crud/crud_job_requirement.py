from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.job_requirement import (
    JobRequiredSkill,
    JobRequiredCertification
)
from app.schemas.job_requirement import (
    JobRequiredSkillCreate,
    JobRequiredCertificationCreate
)


class CRUDJobRequiredSkill(CRUDBase[
    JobRequiredSkill,
    JobRequiredSkillCreate,
    JobRequiredSkillCreate
]):
    def get_by_job(
        self, db: Session, *, job_id: int
    ) -> List[JobRequiredSkill]:
        return db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()


class CRUDJobRequiredCertification(CRUDBase[
    JobRequiredCertification,
    JobRequiredCertificationCreate,
    JobRequiredCertificationCreate
]):
    def get_by_job(
        self, db: Session, *, job_id: int
    ) -> List[JobRequiredCertification]:
        return db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()


job_required_skill = CRUDJobRequiredSkill(JobRequiredSkill)
job_required_certification = CRUDJobRequiredCertification(
    JobRequiredCertification
) 
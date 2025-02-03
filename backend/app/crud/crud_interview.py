from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    def get_by_candidate(
        self,
        db: Session,
        *,
        candidate_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        return (
            db.query(Interview)
            .filter(Interview.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_interviewer(
        self,
        db: Session,
        *,
        interviewer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interview]:
        return (
            db.query(Interview)
            .filter(Interview.interviewer_id == interviewer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_scheduled_interviews(
        self,
        db: Session,
        *,
        start_time: datetime,
        end_time: datetime
    ) -> List[Interview]:
        return (
            db.query(Interview)
            .filter(
                Interview.schedule_time >= start_time,
                Interview.schedule_time <= end_time
            )
            .all()
        )


interview = CRUDInterview(Interview) 
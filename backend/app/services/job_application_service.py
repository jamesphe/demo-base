from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.core.security import get_current_user_id
from fastapi import HTTPException


class JobApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create_application(
        self,
        job_id: int,
        application_in: schemas.JobApplicationCreate,
        user_id: int
    ) -> models.JobApplication:
        """创建职位申请"""
        # 检查职位是否存在且状态为已发布
        job = crud.job.get(self.db, id=job_id)
        if not job or job.status != "published":
            raise HTTPException(
                status_code=404,
                detail="职位不存在或未发布"
            )
        
        # 检查是否已经申请过
        existing = self.get_application_by_job_and_resume(
            job_id,
            application_in.resume_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="已经申请过该职位"
            )

        # 创建申请记录
        application = crud.job_application.create(
            self.db,
            obj_in=application_in
        )
        return application

    def get_application_by_job_and_resume(
        self,
        job_id: int,
        resume_id: int
    ) -> Optional[models.JobApplication]:
        """根据职位ID和简历ID获取申请记录"""
        return self.db.query(models.JobApplication).filter(
            models.JobApplication.job_id == job_id,
            models.JobApplication.resume_id == resume_id
        ).first()

    def get_applications_by_job(
        self,
        job_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.JobApplication]:
        """获取职位的所有申请记录"""
        return crud.job_application.get_by_job(
            self.db,
            job_id=job_id
        )

    def get_applications_by_resume(
        self,
        resume_id: int
    ) -> List[models.JobApplication]:
        """获取简历的所有申请记录"""
        return crud.job_application.get_by_resume(
            self.db,
            resume_id=resume_id
        )

    def update_application_status(
        self,
        application_id: int,
        status: str,
        review_notes: Optional[str] = None,
        current_user: models.User = None
    ) -> models.JobApplication:
        """更新申请状态"""
        application = crud.job_application.get(
            self.db,
            id=application_id
        )
        if not application:
            raise HTTPException(
                status_code=404,
                detail="申请记录不存在"
            )

        # 检查权限
        job = crud.job.get(self.db, id=application.job_id)
        if not current_user.is_superuser and (
            job.tenant_id != current_user.tenant_id
        ):
            raise HTTPException(
                status_code=403,
                detail="无权更新该申请状态"
            )

        return crud.job_application.update_status(
            self.db,
            application_id=application_id,
            status=status,
            review_notes=review_notes
        ) 
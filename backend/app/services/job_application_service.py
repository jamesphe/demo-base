from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud, models, schemas
from fastapi import HTTPException
from app.models.job_application import JobApplication


class JobApplicationService:
    def create_application(
        self,
        db: Session,
        *,
        application_in: schemas.JobApplicationCreate,
        tenant_id: int,
        created_by: int
    ) -> JobApplication:
        """创建职位申请"""
        return crud.job_application.create_with_owner(
            db=db,
            obj_in=application_in,
            tenant_id=tenant_id,
            created_by=created_by
        )
    
    def get_application(
        self,
        db: Session,
        *,
        application_id: int
    ) -> Optional[JobApplication]:
        """获取职位申请"""
        return crud.job_application.get(db=db, id=application_id)
    
    def get_application_with_resume(
        self,
        db: Session,
        *,
        application_id: int
    ) -> Optional[JobApplication]:
        """获取职位申请（包含简历信息）"""
        return crud.job_application.get_with_resume(db=db, id=application_id)
    
    def update_application(
        self,
        db: Session,
        *,
        application_id: int,
        application_in: schemas.JobApplicationUpdate
    ) -> Optional[JobApplication]:
        """更新职位申请"""
        application = crud.job_application.get(db=db, id=application_id)
        if not application:
            return None
        return crud.job_application.update(
            db=db,
            db_obj=application,
            obj_in=application_in
        )
    
    def delete_application(
        self,
        db: Session,
        *,
        application_id: int
    ) -> Optional[JobApplication]:
        """删除职位申请"""
        return crud.job_application.remove(db=db, id=application_id)
    
    def get_applications_by_job(
        self,
        db: Session,
        *,
        job_id: int
    ) -> List[JobApplication]:
        """获取指定职位的所有申请"""
        return crud.job_application.get_by_job(db=db, job_id=job_id)
    
    def get_applications_by_job_with_resume_info(
        self,
        db: Session,
        *,
        job_id: int
    ) -> List[Dict[str, Any]]:
        """获取指定职位的所有申请（包含简历基本信息）"""
        return crud.job_application.get_by_job_with_resume_info(
            db=db, job_id=job_id)
    
    def get_applications_by_resume(
        self,
        db: Session,
        *,
        resume_id: int
    ) -> List[JobApplication]:
        """获取指定简历的所有申请"""
        return crud.job_application.get_by_resume(db=db, resume_id=resume_id)
    
    def get_applications_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobApplication]:
        """获取指定租户的所有职位申请"""
        return crud.job_application.get_by_tenant(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit
        )
    
    def get_applications_by_tenant_with_resume_info(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取指定租户的所有职位申请（包含简历基本信息）"""
        return crud.job_application.get_by_tenant_with_resume_info(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit
        )
    
    def get_applications_by_status(
        self,
        db: Session,
        *,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobApplication]:
        """获取指定状态的所有职位申请"""
        return crud.job_application.get_by_status(
            db=db,
            status=status,
            skip=skip,
            limit=limit
        )
    
    def check_application_exists(
        self,
        db: Session,
        *,
        job_id: int,
        resume_id: int
    ) -> bool:
        """检查是否已经申请过该职位"""
        application = crud.job_application.get_by_job_and_resume(
            db=db,
            job_id=job_id,
            resume_id=resume_id
        )
        return application is not None

    def update_application_status(
        self,
        db: Session,
        *,
        application_id: int,
        status: str,
        review_notes: Optional[str] = None,
        current_user: models.User = None
    ) -> models.JobApplication:
        """更新申请状态"""
        application = crud.job_application.get(
            db,
            id=application_id
        )
        if not application:
            raise HTTPException(
                status_code=404,
                detail="申请记录不存在"
            )

        # 检查权限
        job = crud.job.get(db, id=application.job_id)
        if not current_user.is_superuser and (
            job.tenant_id != current_user.tenant_id
        ):
            raise HTTPException(
                status_code=403,
                detail="无权更新该申请状态"
            )

        return crud.job_application.update_status(
            db,
            application_id=application_id,
            status=status,
            review_notes=review_notes
        )

    async def create_application_with_validation(
        self,
        db: Session,
        application_in: schemas.JobApplicationCreate,
        tenant_id: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> models.JobApplication:
        """创建职位申请（带验证）"""
        # 检查职位是否存在
        job = crud.job.get(db=db, id=application_in.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
        
        # 检查简历是否存在
        resume = crud.resume.get(db=db, id=application_in.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 检查是否已经申请过该职位
        if self.check_application_exists(
            db=db, 
            job_id=application_in.job_id, 
            resume_id=application_in.resume_id
        ):
            raise HTTPException(
                status_code=400, 
                detail="已经申请过该职位"
            )
        
        # 创建职位申请
        application = self.create_application(
            db=db,
            application_in=application_in,
            tenant_id=tenant_id,
            created_by=created_by or application_in.created_by
        )
        
        # 在方法内部导入以避免循环导入
        from app.services.resume_job_matching_service import resume_job_matching_service
        await resume_job_matching_service.analyze_and_update_match(
            db=db,
            application_id=application.id
        )
        
        return application


# 创建服务实例
job_application_service = JobApplicationService()

# 只导出实例
__all__ = ["job_application_service"]
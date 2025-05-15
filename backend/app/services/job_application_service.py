from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app import crud, models, schemas
from fastapi import HTTPException
from app.models.job_application import JobApplication
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from datetime import datetime
from .base import BaseService


class JobApplicationService(BaseService[models.JobApplication, schemas.JobApplicationCreate, schemas.JobApplicationUpdate]):
    """职位申请服务"""
    
    def __init__(self):
        super().__init__(models.JobApplication)

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
        job_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取职位的所有申请"""
        applications = db.query(models.JobApplication).filter(
            models.JobApplication.job_id == job_id
        ).offset(skip).limit(limit).all()
        
        result = []
        for app in applications:
            resume = db.query(models.Resume).filter(
                models.Resume.id == app.resume_id
            ).first()
            
            result.append({
                "application_id": app.id,
                "resume_title": resume.title if resume else None,
                "status": app.status,
                "created_at": app.created_at
            })
            
        return result
    
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
    
    def get_applications_by_tenant_with_resume_info_and_count(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取指定租户的所有职位申请（包含简历基本信息）及总数"""
        # 构建基础查询
        query = (
            db.query(
                models.JobApplication,
                models.Resume,
                models.Job,
                models.User.username.label('publisher_name'),
                models.Tenant.tenant_name.label('tenant_name')
            )
            .join(
                models.Resume,
                models.JobApplication.resume_id == models.Resume.id
            )
            .join(
                models.Job,
                models.JobApplication.job_id == models.Job.id
            )
            .join(
                models.User,
                models.Job.publisher_id == models.User.id
            )
            .join(
                models.Tenant,
                models.Job.tenant_id == models.Tenant.id
            )
        )

        # 如果不是超级管理员，则添加租户过滤条件
        if tenant_id is not None:
            query = query.filter(models.JobApplication.tenant_id == tenant_id)

        # 应用搜索条件
        if filters:
            if filters.get("status"):
                query = query.filter(
                    models.JobApplication.status == filters["status"]
                )
            if filters.get("job_title"):
                query = query.filter(
                    models.Job.title.ilike(f"%{filters['job_title']}%")
                )
            if filters.get("candidate_name"):
                query = query.filter(
                    models.Resume.name.ilike(f"%{filters['candidate_name']}%")
                )
            if filters.get("education"):
                # 学历中英文映射
                education_map = {
                    "college": "大专",
                    "bachelor": "本科",
                    "master": "硕士",
                    "phd": "博士"
                }
                education_value = education_map.get(filters["education"].lower())
                if education_value:
                    query = query.filter(
                        models.Resume.highest_education == education_value
                    )
            if filters.get("experience"):
                # 处理工作经验范围
                if filters["experience"] == "fresh":
                    query = query.filter(
                        models.Resume.experience_years == 0
                    )
                elif filters["experience"] == "0-1":
                    query = query.filter(
                        models.Resume.experience_years < 1
                    )
                elif filters["experience"] == "1-3":
                    query = query.filter(
                        models.Resume.experience_years >= 1,
                        models.Resume.experience_years < 3
                    )
                elif filters["experience"] == "3-5":
                    query = query.filter(
                        models.Resume.experience_years >= 3,
                        models.Resume.experience_years < 5
                    )
                elif filters["experience"] == "5-10":
                    query = query.filter(
                        models.Resume.experience_years >= 5,
                        models.Resume.experience_years < 10
                    )
                elif filters["experience"] == "10+":
                    query = query.filter(
                        models.Resume.experience_years >= 10
                    )
            if filters.get("match_score"):
                # 处理匹配度范围
                if filters["match_score"] == "80+":
                    query = query.filter(
                        models.JobApplication.match_score >= 80
                    )
                elif filters["match_score"] == "60-80":
                    query = query.filter(
                        models.JobApplication.match_score >= 60,
                        models.JobApplication.match_score < 80
                    )
                elif filters["match_score"] == "0-60":
                    query = query.filter(
                        models.JobApplication.match_score < 60
                    )
            if filters.get("apply_time_start"):
                query = query.filter(
                    models.JobApplication.apply_time >= filters["apply_time_start"]
                )
            if filters.get("apply_time_end"):
                query = query.filter(
                    models.JobApplication.apply_time <= filters["apply_time_end"]
                )

        # 应用排序
        if sort_field and sort_order:
            # 定义排序字段映射
            sort_field_map = {
                "id": models.JobApplication.id,
                "job_title": models.Job.title,
                "resume_name": models.Resume.file_name,
                "experience_years": models.Resume.experience_years,
                "apply_time": models.JobApplication.apply_time,
                "status": models.JobApplication.status,
                "match_score": models.JobApplication.match_score
            }
            
            # 获取排序字段
            sort_column = sort_field_map.get(sort_field)
            if sort_column:
                # 应用排序
                if sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                # 默认按申请时间倒序
                query = query.order_by(models.JobApplication.apply_time.desc())

        # 获取总数
        total = query.count()

        # 应用分页
        applications = query.offset(skip).limit(limit).all()

        # 转换结果
        result = [
            {
                "id": application.JobApplication.id,
                "job_id": application.JobApplication.job_id,
                "resume_id": application.JobApplication.resume_id,
                "status": application.JobApplication.status,
                "created_at": application.JobApplication.created_at,
                "updated_at": application.JobApplication.updated_at,
                "apply_time": application.JobApplication.apply_time,
                "tenant_id": application.JobApplication.tenant_id,
                "candidate_name": application.Resume.name,
                "resume_name": application.Resume.file_name,
                "resume_phone": application.Resume.phone,
                "resume_email": application.Resume.email,
                "resume_highest_education": application.Resume.highest_education,
                "resume_experience_years": application.Resume.experience_years,
                "match_score": application.JobApplication.match_score,
                "match_reason": application.JobApplication.match_reason,
                "resume": {
                    "id": application.Resume.id,
                    "name": application.Resume.name,
                    "phone": application.Resume.phone,
                    "email": application.Resume.email,
                    "file_name": application.Resume.file_name,
                    "file_path": application.Resume.file_path,
                    "file_type": application.Resume.file_type,
                },
                "job": {
                    "id": application.Job.id,
                    "title": application.Job.title,
                    "department_name": application.Job.department,
                    "publisher_name": application.publisher_name,
                },
                "tenant_name": application.tenant_name,
            }
            for application in applications
        ]

        return result, total
    
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
        if current_user is not None:
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
        from app.services.resume_job_matching_service import (
            resume_job_matching_service
        )
        await resume_job_matching_service.analyze_and_update_match(
            db=db,
            application_id=application.id
        )
        
        return application

    def get_applications_by_status_and_count(
        self,
        db: Session,
        *,
        status: str,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[JobApplication], int]:
        """获取指定状态和租户的所有职位申请及总数"""
        applications = db.query(self.model).filter(
            models.JobApplication.status == status,
            models.JobApplication.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
        
        # 获取总数
        total = db.query(models.JobApplication).filter(
            models.JobApplication.status == status,
            models.JobApplication.tenant_id == tenant_id
        ).count()
        
        return applications, total

    def get_application_details(
        self,
        db: Session,
        *,
        application_id: int
    ) -> Dict[str, Any]:
        """获取申请详情"""
        application = self.get(db, id=application_id)
        if not application:
            raise HTTPException(status_code=404, detail="申请不存在")
            
        resume = db.query(models.Resume).filter(
            models.Resume.id == application.resume_id
        ).first()
        
        job = db.query(models.Job).filter(
            models.Job.id == application.job_id
        ).first()
        
        return {
            "application_id": application.id,
            "resume_title": resume.title if resume else None,
            "job_title": job.title if job else None,
            "status": application.status,
            "created_at": application.created_at,
            "updated_at": application.updated_at
        }


# 创建服务实例
job_application_service = JobApplicationService()

# 只导出实例
__all__ = ["job_application_service"]
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.job_application import JobApplication
from app import models  # 导入所有模型
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate
)
from app.models.resume import Resume


class CRUDJobApplication(
    CRUDBase[JobApplication, JobApplicationCreate, JobApplicationUpdate]
):
    def get_by_job(
        self, db: Session, *, job_id: int
    ) -> List[JobApplication]:
        """获取指定职位的所有申请"""
        return db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()

    def get_by_resume(
        self, db: Session, *, resume_id: int
    ) -> List[JobApplication]:
        """获取指定简历的所有申请"""
        return db.query(self.model).filter(
            self.model.resume_id == resume_id
        ).all()

    def get_by_job_and_resume(
        self, db: Session, *, job_id: int, resume_id: int
    ) -> Optional[JobApplication]:
        """检查是否已经申请过该职位"""
        return db.query(self.model).filter(
            self.model.job_id == job_id,
            self.model.resume_id == resume_id
        ).first()

    def get_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定租户的所有职位申请"""
        return db.query(self.model).filter(
            self.model.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()

    def get_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定状态的所有职位申请"""
        return db.query(self.model).filter(
            self.model.status == status
        ).offset(skip).limit(limit).all()

    def update_status(
        self,
        db: Session,
        *,
        application_id: int,
        status: str,
        review_notes: Optional[str] = None
    ) -> JobApplication:
        """更新职位申请状态"""
        application = self.get(db, id=application_id)
        if not application:
            return None
        
        update_data = {
            "status": status,
            "review_time": datetime.utcnow(),
            "review_notes": review_notes
        }
        return super().update(db, db_obj=application, obj_in=update_data)

    def create_with_owner(
        self, 
        db: Session, 
        *, 
        obj_in: JobApplicationCreate, 
        tenant_id: int,
        created_by: int
    ) -> JobApplication:
        """创建职位申请"""
        db_obj = JobApplication(
            job_id=obj_in.job_id,
            resume_id=obj_in.resume_id,
            status=obj_in.status if obj_in.status else "pending",
            tenant_id=tenant_id,
            created_by=created_by,
            apply_time=datetime.utcnow(),
            review_notes=obj_in.review_notes if hasattr(obj_in, "review_notes") else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[JobApplication]:
        """获取指定租户的所有职位申请"""
        return self.get_by_tenant(db=db, tenant_id=tenant_id, skip=skip, limit=limit)

    def get_with_resume(
        self, db: Session, *, id: int
    ) -> Optional[JobApplication]:
        """获取职位申请信息，包含完整简历信息"""
        return db.query(self.model).filter(
            self.model.id == id
        ).options(
            joinedload(self.model.resume)
        ).first()

    def get_by_job_with_resume_info(
        self, db: Session, *, job_id: int
    ) -> List[Dict[str, Any]]:
        """获取指定职位的所有申请，包含简历基本信息"""
        # 首先获取所有申请
        applications = db.query(self.model).filter(
            self.model.job_id == job_id
        ).all()
        
        result = []
        for app in applications:
            # 获取关联的简历
            resume = db.query(Resume).filter(
                Resume.id == app.resume_id
            ).first()
            
            # 构建包含简历信息的字典
            app_dict = app.__dict__.copy()
            if "_sa_instance_state" in app_dict:
                del app_dict["_sa_instance_state"]
            
            # 添加简历信息
            if resume:
                # 使用文件名作为简历名称
                app_dict["resume_name"] = resume.filename if hasattr(resume, "filename") else ""
                app_dict["candidate_name"] = resume.name if hasattr(resume, "name") else ""  # 使用简历名称作为候选人名称
                app_dict["candidate_email"] = resume.email if hasattr(resume, "email") else None
                app_dict["candidate_phone"] = resume.phone if hasattr(resume, "phone") else None
            else:
                app_dict["resume_name"] = ""
                app_dict["candidate_name"] = ""
                app_dict["candidate_email"] = None
                app_dict["candidate_phone"] = None
            
            result.append(app_dict)
        
        return result

    def get_by_tenant_with_resume_info(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取指定租户的所有职位申请，包含简历基本信息"""
        # 首先获取所有申请
        applications = db.query(self.model).filter(
            self.model.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
        
        result = []
        for app in applications:
            # 获取关联的简历
            resume = db.query(Resume).filter(
                Resume.id == app.resume_id
            ).first()
            
            # 构建包含简历信息的字典
            app_dict = app.__dict__.copy()
            if "_sa_instance_state" in app_dict:
                del app_dict["_sa_instance_state"]
            
            # 添加简历信息
            if resume:
                # 使用文件名作为简历名称
                app_dict["resume_name"] = resume.filename if hasattr(resume, "filename") else ""
                app_dict["candidate_name"] = resume.name if hasattr(resume, "name") else ""  # 使用简历名称作为候选人名称
                app_dict["candidate_email"] = resume.email if hasattr(resume, "email") else None
                app_dict["candidate_phone"] = resume.phone if hasattr(resume, "phone") else None
            else:
                app_dict["resume_name"] = ""
                app_dict["candidate_name"] = ""
                app_dict["candidate_email"] = None
                app_dict["candidate_phone"] = None
            
            result.append(app_dict)
        
        return result


job_application = CRUDJobApplication(JobApplication) 
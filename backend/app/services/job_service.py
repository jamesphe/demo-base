from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.job import JobCreate, JobUpdate
from .base import BaseService
from app.core.security import get_password_hash
from app.core.config import settings
from app import crud
from app.services.job_requirement_service import JobRequirementService


class JobService(BaseService[models.Job, JobCreate, JobUpdate]):
    """职位服务"""
    
    def __init__(self):
        """初始化服务"""
        super().__init__(models.Job)

    def search_jobs(
        self,
        db: Session,
        *,
        keyword: str = None,
        tenant_id: Optional[int] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        experience_level: Optional[str] = None,
        education_level: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Job]:
        """搜索职位"""
        query = db.query(models.Job)
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(models.Job.tenant_id == tenant_id)
        if department:
            filters.append(models.Job.department == department)
        if status:
            filters.append(models.Job.status == status)
        if experience_level:
            filters.append(models.Job.experience_level == experience_level)
        if education_level:
            filters.append(models.Job.education_level == education_level)
        if start_date:
            filters.append(models.Job.created_at >= start_date)
        if end_date:
            filters.append(models.Job.created_at <= end_date)
            
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                models.Job.title.ilike(f"%{keyword}%"),
                models.Job.description.ilike(f"%{keyword}%"),
                models.Job.requirements.ilike(f"%{keyword}%"),
                models.Job.responsibilities.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
            
        # 技能要求过滤
        if required_skills:
            for skill in required_skills:
                filters.append(models.Job.required_skills.contains([skill]))
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

    async def get_job_statistics(
        self,
        db: Session,
        *,
        job_id: int
    ) -> Dict[str, Any]:
        """获取职位统计信息"""
        job = self.get(db, id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
            
        # 获取候选人统计
        candidates = db.query(models.Candidate).filter(
            models.Candidate.job_id == job_id
        ).all()
        
        # 统计各状态候选人数量
        status_counts = {}
        for candidate in candidates:
            status_counts[candidate.status] = status_counts.get(candidate.status, 0) + 1
            
        # 获取面试统计
        interviews = db.query(models.Interview).filter(
            models.Interview.job_id == job_id
        ).all()
        
        # 统计面试情况
        interview_stats = {
            "total": len(interviews),
            "scheduled": len([i for i in interviews if i.status == "scheduled"]),
            "completed": len([i for i in interviews if i.status == "completed"]),
            "cancelled": len([i for i in interviews if i.status == "cancelled"]),
            "avg_score": sum(i.evaluation_score or 0 for i in interviews) / len(interviews) if interviews else 0
        }
        
        return {
            "total_candidates": len(candidates),
            "candidate_status": status_counts,
            "interview_stats": interview_stats,
            "created_at": job.created_at,
            "last_updated": job.updated_at
        }

    async def match_candidates(
        self,
        db: Session,
        *,
        job_id: int,
        min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """匹配合适的候选人"""
        job = self.get(db, id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
            
        # 获取同一租户下的所有候选人
        candidates = db.query(models.Candidate).filter(
            models.Candidate.tenant_id == job.tenant_id,
            models.Candidate.status.in_(["new", "pending", "interviewed"])
        ).all()
        
        matches = []
        for candidate in candidates:
            # TODO: 实现匹配算法
            match_score = 0.0  # 计算匹配度
            
            if match_score >= min_score:
                matches.append({
                    "candidate_id": candidate.id,
                    "name": candidate.name,
                    "match_score": match_score,
                    "match_reasons": ["匹配原因..."],
                    "current_status": candidate.status
                })
        
        # 按匹配度排序
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)

    async def update_job_status(
        self,
        db: Session,
        *,
        job_id: int,
        status: str,
        note: Optional[str] = None
    ) -> models.Job:
        """更新职位状态"""
        job = self.get(db, id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
            
        # 创建状态变更记录
        status_change = models.JobStatusChange(
            job_id=job_id,
            from_status=job.status,
            to_status=status,
            note=note,
            created_at=datetime.utcnow()
        )
        db.add(status_change)
        
        # 更新职位状态
        job = self.update(
            db,
            db_obj=job,
            obj_in=JobUpdate(
                status=status,
                status_updated_at=datetime.utcnow()
            )
        )
        
        return job

    def create_job(
        self,
        db: Session,
        job_in: schemas.JobCreate,
        tenant_id: int,
        publisher_id: int
    ) -> models.Job:
        """创建职位"""
        # 检查 external_id 是否已存在
        if job_in.external_id:
            existing_job = self.get_job_by_external_id(db, job_in.external_id)
            if existing_job:
                raise ValueError(f"Job with external_id {job_in.external_id} already exists")
        
        # 准备职位基础数据
        job_data = job_in.model_dump(exclude={
            'required_skills',
            'required_certifications'
        })
        job_data.update({
            "tenant_id": tenant_id,
            "publisher_id": publisher_id,
            "status": "draft"
        })
        
        # 创建职位
        job = crud.job.create(db, obj_in=job_data)
        
        # 处理技能要求
        if job_in.required_skills:
            for skill_data in job_in.required_skills:
                required_skill = models.JobRequiredSkill(
                    job_id=job.id,
                    skill_id=skill_data["skill_id"],
                    skill_level=skill_data["skill_level"],
                    is_required=skill_data["is_required"]
                )
                db.add(required_skill)
        
        # 处理证书要求
        if job_in.required_certifications:
            for cert_data in job_in.required_certifications:
                required_cert = models.JobRequiredCertification(
                    job_id=job.id,
                    certification_id=cert_data["certification_id"],
                    is_required=cert_data["is_required"]
                )
                db.add(required_cert)
        
        db.commit()
        db.refresh(job)
        return job

    def get_job(
        self,
        db: Session,
        job_id: int
    ) -> Optional[models.Job]:
        """获取职位详情"""
        return db.query(models.Job).filter(models.Job.id == job_id).first()

    def list_jobs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None
    ) -> List[models.Job]:
        """获取职位列表"""
        query = db.query(models.Job)
        if tenant_id:
            query = query.filter(models.Job.tenant_id == tenant_id)
        return query.offset(skip).limit(limit).all()

    def update_job(
        self,
        db: Session,
        job_id: int,
        job_in: schemas.JobUpdate,
        skills: Optional[List[schemas.JobRequiredSkillCreate]] = None,
        certifications: Optional[List[schemas.JobRequiredCertificationCreate]] = None
    ) -> models.Job:
        """更新职位信息"""
        job = crud.job.get(db, id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")

        # 更新职位基本信息
        job = crud.job.update(db, db_obj=job, obj_in=job_in)

        # 更新技能要求
        if skills is not None:  # 允许清空技能要求
            requirement_service = JobRequirementService(db)
            requirement_service.update_job_skills(job.id, skills)

        # 更新证书要求
        if certifications is not None:  # 允许清空证书要求
            requirement_service = JobRequirementService(db)
            requirement_service.update_job_certifications(job.id, certifications)

        return job

    def delete_job(self, job_id: int) -> bool:
        """删除职位"""
        job = self.get_job(job_id)
        if not job:
            return False

        self.db.delete(job)
        self.db.commit()
        return True

    def publish_job(self, job_id: int) -> Optional[models.Job]:
        """发布职位"""
        job = self.get_job(job_id)
        if not job:
            return None

        job.status = "published"
        job.published_at = datetime.utcnow()
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def close_job(self, job_id: int) -> Optional[models.Job]:
        """关闭职位"""
        job = self.get_job(job_id)
        if not job:
            return None

        job.status = "closed"
        job.closed_at = datetime.utcnow()
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_with_requirements(self, job_id: int) -> dict:
        """获取职位信息及其要求"""
        job = crud.job.get(self.db, id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")

        requirement_service = JobRequirementService(self.db)
        requirements = requirement_service.get_job_requirements(job_id)

        return {
            "job": job,
            "requirements": requirements
        }

    def get_job_by_external_id(self, db: Session, external_id: str) -> Optional[models.Job]:
        return crud.job.get_by_external_id(db, external_id=external_id)

# 创建服务实例
job_service = JobService()

# 只导出实例
__all__ = ["job_service"] 
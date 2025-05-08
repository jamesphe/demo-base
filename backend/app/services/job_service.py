from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from app import models, schemas, crud
from app.schemas.job import JobCreate, JobUpdate
from app.services.base import BaseService
from app.core.security import get_password_hash
from app.core.config import settings
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
        *,
        job_in: JobCreate,
        tenant_id: int,
        publisher_id: int
    ) -> models.Job:
        """创建职位"""
        # 检查外部ID是否已存在
        if job_in.external_id:
            existing_job = self.get_job_by_external_id(db, job_in.external_id)
            if existing_job:
                raise ValueError(
                    f"Job with external_id {job_in.external_id} already exists"
                )
        
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

    def get_job(self, db: Session, *, job_id: int) -> Optional[models.Job]:
        """获取职位信息"""
        # 使用 joinedload 优化关联查询
        job = db.query(models.Job).options(
            joinedload(models.Job.keywords)
        ).filter(models.Job.id == job_id).first()
        
        if job:
            # 添加tenant_name字段
            tenant = db.query(models.Tenant).filter(
                models.Tenant.id == job.tenant_id
            ).first()
            if tenant:
                # 动态添加tenant_name属性
                job.tenant_name = tenant.tenant_name
            
            # 检查是否有邮箱同步配置
            has_email_sync = len(job.keywords) > 0
            receiving_email = None
            
            if has_email_sync and job.keywords:
                # 获取第一个关键字的邮箱信息
                sync_email = db.query(models.ResumeSyncEmail).filter(
                    models.ResumeSyncEmail.id == job.keywords[0].sync_email_id
                ).first()
                
                if sync_email:
                    receiving_email = sync_email.email
            
            # 设置额外属性（不在模型定义中的属性）
            job.emailSyncEnabled = has_email_sync
            job.receivingEmail = receiving_email
            
            # 创建一个新的动态属性来存储关键字字典列表，而不是修改原始的关联关系
            keywords_list = []
            for kw in job.keywords:
                keywords_list.append({
                    'id': kw.id,
                    'job_id': kw.job_id,
                    'sync_email_id': kw.sync_email_id,
                    'keyword': kw.keyword,
                    'description': kw.description,
                    'is_active': kw.is_active,
                    'created_at': kw.created_at,
                    'updated_at': kw.updated_at
                })
            job.keywords_list = keywords_list
            
        return job

    def get_job_by_id(self, db: Session, *, job_id: int) -> Optional[models.Job]:
        """根据ID获取职位"""
        return self.get(db, id=job_id)

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
        *,
        job_id: int,
        job_in: JobUpdate,
        tenant_id: int
    ) -> models.Job:
        """更新职位信息"""
        job = self.get_job(db=db, job_id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")

        # 从job_in中提取keywords
        keywords_data = None
        if hasattr(job_in, 'keywords'):
            keywords_data = job_in.keywords
        
        # 创建更新数据字典，只包含非None值
        update_data = {}
        job_in_dict = job_in.dict(exclude_unset=True)
        
        # 移除keywords字段，手动处理
        if 'keywords' in job_in_dict:
            del job_in_dict['keywords']

        # 只更新前端提交的非空字段  
        for key, value in job_in_dict.items():
            if value is not None:  # 只更新非None值
                update_data[key] = value
                
        # 更新职位基本信息
        if update_data:  # 只有在有更新数据时才更新
            job = crud.job.update(db, db_obj=job, obj_in=update_data)

        # 更新技能要求
        if hasattr(job_in, 'skills') and job_in.skills is not None:  # 允许清空技能要求
            requirement_service = JobRequirementService(db)
            requirement_service.update_job_skills(job.id, job_in.skills)

        # 更新证书要求
        if hasattr(job_in, 'certifications') and job_in.certifications is not None:  # 允许清空证书要求
            requirement_service = JobRequirementService(db)
            requirement_service.update_job_certifications(job.id, job_in.certifications)

        # 更新关键字
        if keywords_data is not None:
            # 首先删除该职位的所有现有关键字
            db.query(models.JobKeyword).filter(
                models.JobKeyword.job_id == job_id
            ).delete()
            
            # 添加新的关键字
            for keyword_data in keywords_data:
                keyword = models.JobKeyword(
                    job_id=job_id,
                    keyword=keyword_data["keyword"],
                    sync_email_id=keyword_data["sync_email_id"],
                    description=keyword_data.get("description")
                )
                db.add(keyword)
            
            db.commit()
            db.refresh(job)

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
        """通过外部ID获取职位"""
        return db.query(models.Job).filter(
            models.Job.external_id == external_id
        ).first()

    def create_job_application(self, db: Session, *, obj_in: schemas.JobApplicationCreate) -> models.JobApplication:
        """创建职位申请"""
        return crud.job_application.create(db=db, obj_in=obj_in)

    def list_jobs_with_count(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        **filters
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取职位列表及总数"""
        query = db.query(models.Job)
        
        # 添加租户关联查询
        query = query.join(models.Tenant)
        
        # 应用过滤条件
        if tenant_id:
            query = query.filter(models.Job.tenant_id == tenant_id)
        
        for key, value in filters.items():
            if key == "title":
                query = query.filter(models.Job.title.ilike(f"%{value}%"))
            elif key == "department_id":
                query = query.filter(models.Job.department_id == value)
            elif key == "create_time":
                query = query.filter(models.Job.created_at.between(value[0], value[1]))
            elif key == "status":
                query = query.filter(models.Job.status == value)
        
        # 获取总数
        total = query.count()
        
        # 获取分页数据
        jobs = query.offset(skip).limit(limit).all()
        
        # 转换为字典列表
        job_list = []
        for job in jobs:
            # 获取职位关键字信息
            keywords = db.query(models.JobKeyword).filter(
                models.JobKeyword.job_id == job.id
            ).all()
            
            # 检查是否有邮箱同步配置
            has_email_sync = len(keywords) > 0
            receiving_email = None
            
            if has_email_sync and keywords:
                # 获取第一个关键字的邮箱信息
                sync_email = db.query(models.ResumeSyncEmail).filter(
                    models.ResumeSyncEmail.id == keywords[0].sync_email_id
                ).first()
                
                if sync_email:
                    receiving_email = sync_email.email
            
            job_dict = {
                "id": job.id,
                "external_id": job.external_id,
                "tenant_id": job.tenant_id,
                "tenant_name": job.tenant.tenant_name,  # 使用 tenant_name 替代 company_name
                "publisher_id": job.publisher_id,
                "title": job.title,
                "department": job.department,
                "job_type": job.job_type,
                "headcount": job.headcount,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_type": job.salary_type,
                "salary_structure": job.salary_structure,
                "location": job.location,
                "experience_required": job.experience_required,
                "education_required": job.education_required,
                "description": job.description,
                "requirements": job.requirements,
                "benefits": job.benefits,
                "preferences": job.preferences,
                "status": job.status,
                "created_at": job.created_at,
                "published_at": job.published_at,
                "closed_at": job.closed_at,
                # 添加关键字和邮箱配置信息
                "keywords": [
                    {
                        "id": kw.id,
                        "job_id": kw.job_id,
                        "sync_email_id": kw.sync_email_id,
                        "keyword": kw.keyword,
                        "description": kw.description
                    } for kw in keywords
                ],
                "emailKeywords": ",".join([kw.keyword for kw in keywords]) if keywords else "",
                "emailSyncEnabled": has_email_sync,
                "receivingEmail": receiving_email,
                "tenant": {  # 添加完整的租户信息
                    "id": job.tenant.id,
                    "name": job.tenant.tenant_name,  # 使用 tenant_name 替代 company_name
                    "code": job.tenant.external_id,  # 使用 external_id 作为租户代码
                    "status": job.tenant.status
                }
            }
            job_list.append(job_dict)
        
        return job_list, total

    def get_job_list(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Dict = None
    ) -> Dict[str, Any]:
        """获取职位列表"""
        query = db.query(models.Job).filter(models.Job.tenant_id == tenant_id)
        
        # 应用过滤条件
        if filters:
            for field, value in filters.items():
                if field == 'department' and value:
                    query = query.filter(models.Job.department == value)
                # ... 其他过滤条件 ...
        
        total = query.count()
        jobs = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "items": jobs
        }

# 创建服务实例
job_service = JobService()

# 只导出实例
__all__ = ["job_service"] 
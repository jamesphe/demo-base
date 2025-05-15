from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from .base import BaseService
from app.services import resume_service


class CandidateService(BaseService[models.Candidate, CandidateCreate, CandidateUpdate]):
    """候选人服务"""
    
    def __init__(self):
        super().__init__(models.Candidate)

    def search_candidates(
        self,
        db: Session,
        *,
        keyword: str,
        tenant_id: Optional[int] = None,
        job_id: Optional[int] = None,
        status: Optional[str] = None,
        education_level: Optional[str] = None,
        skills: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Candidate]:
        """搜索候选人"""
        query = db.query(models.Candidate)
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(models.Candidate.tenant_id == tenant_id)
        if job_id is not None:
            filters.append(models.Candidate.job_id == job_id)
        if status:
            filters.append(models.Candidate.status == status)
        if education_level:
            filters.append(models.Candidate.highest_education == education_level)
        if start_date:
            filters.append(models.Candidate.created_at >= start_date)
        if end_date:
            filters.append(models.Candidate.created_at <= end_date)
            
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                models.Candidate.name.ilike(f"%{keyword}%"),
                models.Candidate.email.ilike(f"%{keyword}%"),
                models.Candidate.phone.ilike(f"%{keyword}%"),
                models.Candidate.current_company.ilike(f"%{keyword}%"),
                models.Candidate.graduate_school.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
            
        # 技能过滤
        if skills:
            for skill in skills:
                filters.append(models.Candidate.skills.contains([skill]))
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

    async def create_from_resume(
        self,
        db: Session,
        *,
        resume_id: str,
        job_id: Optional[int] = None
    ) -> models.Candidate:
        """从简历创建候选人"""
        resume = resume_service.get_by_resume_id(db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
            
        # 检查是否已存在相同邮箱或手机的候选人
        existing = db.query(models.Candidate).filter(
            or_(
                models.Candidate.email == resume.email,
                models.Candidate.phone == resume.phone
            )
        ).first()
        
        if existing:
            # 更新现有候选人信息
            candidate = self.update(
                db,
                db_obj=existing,
                obj_in=CandidateUpdate(
                    name=resume.name,
                    email=resume.email,
                    phone=resume.phone,
                    highest_education=resume.highest_education,
                    graduate_school=resume.graduate_school,
                    major=resume.major,
                    skills=resume.skills,
                    job_id=job_id,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            # 创建新候选人
            candidate_in = CandidateCreate(
                name=resume.name,
                email=resume.email,
                phone=resume.phone,
                highest_education=resume.highest_education,
                graduate_school=resume.graduate_school,
                major=resume.major,
                skills=resume.skills,
                tenant_id=resume.tenant_id,
                job_id=job_id,
                status="new"
            )
            candidate = self.create(db=db, obj_in=candidate_in)
        
        # 关联简历
        resume_service.update(
            db,
            db_obj=resume,
            obj_in=schemas.ResumeUpdate(talent_id=candidate.id)
        )
        
        return candidate

    async def update_candidate_status(
        self,
        db: Session,
        *,
        candidate_id: int,
        status: str,
        note: Optional[str] = None
    ) -> models.Candidate:
        """更新候选人状态"""
        candidate = self.get(db, id=candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="候选人不存在")
            
        # 创建状态变更记录
        status_change = models.CandidateStatusChange(
            candidate_id=candidate_id,
            from_status=candidate.status,
            to_status=status,
            note=note,
            created_at=datetime.utcnow()
        )
        db.add(status_change)
        
        # 更新候选人状态
        candidate = self.update(
            db,
            db_obj=candidate,
            obj_in=CandidateUpdate(
                status=status,
                status_updated_at=datetime.utcnow()
            )
        )
        
        return candidate

    def get_status_history(
        self,
        db: Session,
        *,
        candidate_id: int
    ) -> List[Dict[str, Any]]:
        """获取候选人状态变更历史"""
        history = db.query(models.CandidateStatusChange).filter(
            models.CandidateStatusChange.candidate_id == candidate_id
        ).order_by(
            models.CandidateStatusChange.created_at.desc()
        ).all()
        
        return [
            {
                "from_status": h.from_status,
                "to_status": h.to_status,
                "note": h.note,
                "created_at": h.created_at
            }
            for h in history
        ]


# 创建服务实例
candidate_service = CandidateService()

# 只导出实例
__all__ = ["candidate_service"] 
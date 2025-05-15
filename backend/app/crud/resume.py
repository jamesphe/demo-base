from typing import Dict, List, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate


class CRUDResume(CRUDBase[Resume, ResumeCreate, ResumeUpdate]):
    def get_work_experience(self, db: Session, resume_id: int) -> List[Dict[str, Any]]:
        """获取工作经历"""
        resume = self.get(db, id=resume_id)
        if not resume:
            return []
        return resume.work_history if resume.work_history else []

    def get_education(self, db: Session, resume_id: int) -> List[Dict[str, Any]]:
        """获取教育经历"""
        resume = self.get(db, id=resume_id)
        if not resume:
            return []
        return resume.edu_experience if resume.edu_experience else []

    def get_skills(self, db: Session, resume_id: int) -> List[str]:
        """获取技能信息"""
        resume = self.get(db, id=resume_id)
        if not resume:
            return []
        return resume.skills if resume.skills else []

    def get_projects(self, db: Session, resume_id: int) -> List[Dict[str, Any]]:
        """获取项目经历"""
        resume = self.get(db, id=resume_id)
        if not resume:
            return []
        return resume.project_experience if resume.project_experience else []

    def get_resume_with_details(self, db: Session, resume_id: int) -> Optional[Resume]:
        """获取带有详细信息的简历"""
        resume = self.get(db, id=resume_id)
        if not resume:
            return None

        # 确保所有字段都有默认值
        resume.work_history = resume.work_history if resume.work_history else []
        resume.edu_experience = resume.edu_experience if resume.edu_experience else []
        resume.skills = resume.skills if resume.skills else []
        resume.project_experience = resume.project_experience if resume.project_experience else []
        resume.certificates = resume.certificates if resume.certificates else []

        return resume

    def get_by_external_id(self, db: Session, external_id: str) -> Optional[Resume]:
        """通过外部ID获取简历"""
        return db.query(Resume).filter(Resume.external_id == external_id).first()

    def get_by_tenant(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """获取租户的所有简历"""
        return (
            db.query(Resume)
            .filter(Resume.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_resumes(
        self,
        db: Session,
        *,
        keyword: str = None,
        tenant_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resume]:
        """搜索简历"""
        query = db.query(Resume)
        
        # 基础过滤条件
        filters = []
        if tenant_id is not None:
            filters.append(Resume.tenant_id == tenant_id)
        if status:
            filters.append(Resume.processing_status == status)
            
        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                Resume.name.ilike(f"%{keyword}%"),
                Resume.email.ilike(f"%{keyword}%"),
                Resume.phone.ilike(f"%{keyword}%"),
                Resume.content.ilike(f"%{keyword}%")
            )
            filters.append(keyword_filter)
            
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()


resume = CRUDResume(Resume) 
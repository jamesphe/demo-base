from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_, or_

from app import models, schemas
from app.services.base import BaseService


class ResumeRepositoryService(BaseService[models.ResumeRepository, 
                                       schemas.ResumeRepositoryCreate,
                                       schemas.ResumeRepositoryUpdate]):
    """简历库服务"""
    
    def __init__(self):
        """初始化服务"""
        super().__init__(model_class=models.ResumeRepository)

    async def create_repository(
        self,
        db: Session,
        *,
        name: str,
        resume_type: str,
        description: Optional[str] = None,
        tenant_id: Optional[int] = None
    ) -> models.ResumeRepository:
        """创建简历库"""
        # 检查名称是否已存在
        existing = self.get_by_name(db, name=name, tenant_id=tenant_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="简历库名称已存在"
            )
            
        repository_in = schemas.ResumeRepositoryCreate(
            name=name,
            resume_type=resume_type,
            description=description,
            tenant_id=tenant_id
        )
        
        return self.create(db=db, obj_in=repository_in)

    def get_by_name(
        self,
        db: Session,
        *,
        name: str,
        tenant_id: Optional[int] = None
    ) -> Optional[models.ResumeRepository]:
        """根据名称获取简历库"""
        query = db.query(models.ResumeRepository).filter(
            models.ResumeRepository.name == name
        )
        if tenant_id is not None:
            query = query.filter(
                models.ResumeRepository.tenant_id == tenant_id
            )
        return query.first()

    async def get_repository_detail(
        self,
        db: Session,
        *,
        repository_id: int
    ) -> Dict[str, Any]:
        """获取简历库详情"""
        repository = self.get(db, id=repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="简历库不存在")
            
        # 获取简历统计
        resumes = db.query(models.Resume).filter(
            models.Resume.repository_id == repository_id
        ).all()
        
        # 统计处理状态
        status_counts = {
            "total": len(resumes),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for resume in resumes:
            status = resume.processing_status
            if status in status_counts:
                status_counts[status] += 1
                
        # 统计文件类型
        file_types = {}
        for resume in resumes:
            file_type = resume.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
        return {
            "id": repository.id,
            "name": repository.name,
            "resume_type": repository.resume_type,
            "description": repository.description,
            "tenant_id": repository.tenant_id,
            "created_at": repository.created_at,
            "status_counts": status_counts,
            "file_types": file_types,
            "last_updated": max([r.updated_at for r in resumes]) if resumes else None
        }

    async def get_tenant_repositories(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """获取租户的所有简历库统计信息"""
        repositories = self.get_multi_by_tenant(db, tenant_id=tenant_id)
        
        result = []
        for repo in repositories:
            # 获取简历数量
            resume_count = db.query(models.Resume).filter(
                models.Resume.repository_id == repo.id
            ).count()
            
            # 获取最近更新时间
            latest_resume = db.query(models.Resume).filter(
                models.Resume.repository_id == repo.id
            ).order_by(
                models.Resume.updated_at.desc()
            ).first()
            
            result.append({
                "id": repo.id,
                "name": repo.name,
                "resume_type": repo.resume_type,
                "description": repo.description,
                "resume_count": resume_count,
                "created_at": repo.created_at,
                "last_updated": latest_resume.updated_at if latest_resume else None
            })
            
        return result

    async def merge_repositories(
        self,
        db: Session,
        *,
        source_ids: List[int],
        target_id: int
    ) -> models.ResumeRepository:
        """合并简历库"""
        # 检查目标简历库
        target_repo = self.get(db, id=target_id)
        if not target_repo:
            raise HTTPException(status_code=404, detail="目标简历库不存在")
            
        # 检查源简历库
        for repo_id in source_ids:
            if repo_id == target_id:
                continue
                
            source_repo = self.get(db, id=repo_id)
            if not source_repo:
                raise HTTPException(
                    status_code=404,
                    detail=f"源简历库 {repo_id} 不存在"
                )
                
            if source_repo.tenant_id != target_repo.tenant_id:
                raise HTTPException(
                    status_code=400,
                    detail="只能合并同一租户的简历库"
                )
                
            # 更新简历关联
            db.query(models.Resume).filter(
                models.Resume.repository_id == repo_id
            ).update({
                "repository_id": target_id,
                "updated_at": datetime.utcnow()
            })
            
            # 删除源简历库
            self.remove(db=db, id=repo_id)
            
        return target_repo

    def get_repository(self, db: Session, repository_id: int) -> Optional[models.ResumeRepository]:
        """获取简历库（get方法的别名）"""
        return self.get(db, id=repository_id)


# 创建服务实例
repository_service = ResumeRepositoryService()

# 只导出实例
__all__ = ["repository_service"] 
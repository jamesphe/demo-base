from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
import shutil
from datetime import datetime

from app import crud, models, schemas
from app.core.config import settings
from app.models.resume_repository import ResumeRepository
from app.schemas.resume_repository import ResumeRepositoryCreate
from app.services import resume_service


class RepositoryService:
    """简历库服务"""
    
    async def create_repository(
        self,
        db: Session,
        *,
        name: str,
        resume_type: str,
        description: Optional[str] = None,
        tenant_id: int
    ) -> models.ResumeRepository:
        """创建新的简历库"""
        # 检查同名简历库
        if crud.repository.get_by_name(db, name=name):
            raise ValueError("该简历库名称已存在")
        
        repository_in = schemas.ResumeRepositoryCreate(
            name=name,
            resume_type=resume_type,
            description=description,
            tenant_id=tenant_id
        )
        repository = crud.repository.create(db=db, obj_in=repository_in)
        return repository

    async def get_repository_stats(db: Session) -> Dict[str, Any]:
        """获取简历库统计信息(超级管理员)"""
        repositories = crud.repository.get_multi(db)
        
        total_resumes = 0
        repository_stats = []
        
        for repo in repositories:
            resume_count = len(crud.resume.get_by_repository(db, repository_id=repo.id))
            total_resumes += resume_count
            repository_stats.append({
                "id": repo.id,
                "name": repo.name,
                "resume_count": resume_count,
                "resume_type": repo.resume_type,
                "created_at": repo.created_at
            })
        
        return {
            "total_repositories": len(repositories),
            "total_resumes": total_resumes,
            "repositories": repository_stats
        }

    async def get_repository_stats_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int
    ) -> Dict[str, Any]:
        """获取指定租户的简历库统计信息"""
        repositories = crud.repository.get_multi_by_tenant(db, tenant_id=tenant_id)
        
        total_resumes = 0
        repository_stats = []
        
        for repo in repositories:
            resume_count = len(crud.resume.get_by_repository(db, repository_id=repo.id))
            total_resumes += resume_count
            repository_stats.append({
                "id": repo.id,
                "name": repo.name,
                "resume_count": resume_count,
                "resume_type": repo.resume_type,
                "created_at": repo.created_at
            })
        
        return {
            "total_repositories": len(repositories),
            "total_resumes": total_resumes,
            "repositories": repository_stats
        }

    async def get_repository_detail(
        self,
        db: Session,
        repository_id: int,
        list_only: bool = False
    ) -> Dict[str, Any]:
        """获取简历库详细信息"""
        repository = crud.repository.get(db, id=repository_id)
        if not repository:
            raise ValueError("简历库不存在")
        
        resumes = crud.resume.get_by_repository(db, repository_id=repository_id)
        
        # 如果只需要列表,则不返回简历内容
        if list_only:
            resume_list = [
                {
                    "id": resume.id,
                    "file_name": resume.file_name,
                    "file_url": resume.file_url,
                    "created_at": resume.created_at
                }
                for resume in resumes
            ]
        else:
            resume_list = [
                {
                    "id": resume.id,
                    "file_name": resume.file_name,
                    "file_url": resume.file_url,
                    "content": resume.content,
                    "parsed_data": resume.parsed_data,
                    "created_at": resume.created_at
                }
                for resume in resumes
            ]
        
        return {
            "id": repository.id,
            "name": repository.name,
            "resume_type": repository.resume_type,
            "description": repository.description,
            "created_at": repository.created_at,
            "resume_count": len(resumes),
            "resumes": resume_list
        }

    async def delete_repository(
        self,
        db: Session,
        repository_id: int
    ) -> None:
        """删除简历库及其关联的简历文件"""
        repository = crud.repository.get(db, id=repository_id)
        if not repository:
            raise ValueError("简历库不存在")
        
        # 获取所有关联的简历
        resumes = crud.resume.get_by_repository(db, repository_id=repository_id)
        
        # 删除简历文件
        for resume in resumes:
            resume_service.delete_resume_file(resume.file_url)
            crud.resume.remove(db=db, id=resume.id)
        
        # 删除简历库
        crud.repository.remove(db=db, id=repository_id)


# 创建服务实例
repository_service = RepositoryService()

# 只导出实例
__all__ = ["repository_service"] 
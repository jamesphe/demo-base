from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app import crud, models
from app.models.resume_repository import ResumeRepository
from app.schemas.resume_repository import ResumeRepositoryCreate


class RepositoryService:
    async def create_repository(
        self,
        db: Session,
        name: str,
        resume_type: str,
        description: Optional[str] = None
    ) -> ResumeRepository:
        """创建新的简历库"""
        try:
            # 检查是否存在同名简历库
            existing = crud.repository.get_by_name(db, name=name)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="该名称已被使用"
                )

            # 创建简历库
            repository_in = ResumeRepositoryCreate(
                name=name,
                resume_type=resume_type,
                description=description
            )
            repository = crud.repository.create(db=db, obj_in=repository_in)
            return repository

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"创建简历库失败: {str(e)}"
            )

    async def get_repository_stats(
        self,
        db: Session,
        repository_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取简历库统计信息"""
        try:
            query = db.query(models.Resume)
            if repository_id:
                query = query.filter(
                    models.Resume.repository_id == repository_id
                )

            total_resumes = query.count()
            processed_resumes = query.filter(
                models.Resume.processing_status == "success"
            ).count()
            failed_resumes = query.filter(
                models.Resume.processing_status == "failed"
            ).count()

            # 获取本月新增
            current_month_start = datetime.utcnow().replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            monthly_new = query.filter(
                models.Resume.created_at >= current_month_start
            ).count()

            return {
                "total_resumes": total_resumes,
                "processed_resumes": processed_resumes,
                "failed_resumes": failed_resumes,
                "monthly_new": monthly_new,
                "processing_rate": (
                    round(processed_resumes / total_resumes * 100, 2)
                    if total_resumes > 0 else 0
                )
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"获取统计信息失败: {str(e)}"
            )

    async def get_repository_detail(
        self,
        db: Session,
        repository_id: int,
        list_only: bool = False
    ) -> Dict[str, Any]:
        """获取简历库详细信息"""
        try:
            # 获取简历库基本信息
            repository = crud.repository.get(db=db, id=repository_id)
            if not repository:
                raise HTTPException(
                    status_code=404,
                    detail="简历库不存在"
                )

            # 获取统计信息
            stats = await self.get_repository_stats(db, repository_id)

            # 获取简历列表
            resumes = db.query(models.Resume).filter(
                models.Resume.repository_id == repository_id
            ).all()

            resume_list = []
            for resume in resumes:
                resume_info = {
                    "id": resume.id,
                    "name": resume.name,
                    "file_name": resume.file_name,
                    "file_type": resume.file_type,
                    "processing_status": resume.processing_status,
                    "processing_message": resume.processing_message,
                    "processing_error": resume.processing_error,
                    "created_at": resume.created_at
                }
                if not list_only and resume.parsed_data:
                    resume_info["parsed_data"] = resume.parsed_data
                resume_list.append(resume_info)

            return {
                "id": repository.id,
                "name": repository.name,
                "description": repository.description,
                "resume_type": repository.resume_type,
                "created_at": repository.created_at,
                "updated_at": repository.updated_at,
                "stats": stats,
                "resumes": resume_list
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"获取简历库详情失败: {str(e)}"
            )

    async def delete_repository(
        self,
        db: Session,
        repository_id: int
    ) -> bool:
        """删除简历库"""
        try:
            repository = crud.repository.get(db=db, id=repository_id)
            if not repository:
                raise HTTPException(
                    status_code=404,
                    detail="简历库不存在"
                )

            # 删除关联的简历
            resumes = db.query(models.Resume).filter(
                models.Resume.repository_id == repository_id
            ).all()
            for resume in resumes:
                db.delete(resume)

            # 删除简历库
            crud.repository.remove(db=db, id=repository_id)
            await db.commit()

            return True

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"删除简历库失败: {str(e)}"
            ) 
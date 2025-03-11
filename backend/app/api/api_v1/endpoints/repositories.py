from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app import crud, models
from app.api import deps
from datetime import datetime
from app.schemas.resume_repository import ResumeRepository
from app.services.repository_service import RepositoryService

router = APIRouter()
repository_service = RepositoryService()


@router.get("/", response_model=List[ResumeRepository])
def read_repositories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取简历库列表
    """
    repositories = crud.repository.get_multi(db, skip=skip, limit=limit)
    return repositories


@router.post("/", response_model=ResumeRepository)
async def create_repository(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Body(...),
    resume_type: str = Body(...),
    description: Optional[str] = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新简历库
    """
    return await repository_service.create_repository(
        db,
        name=name,
        resume_type=resume_type,
        description=description
    )


@router.get("/statistics")
async def get_repository_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历库统计信息"""
    return await repository_service.get_repository_stats(db)


@router.delete("/{repository_id}")
async def delete_repository(
    repository_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除指定的简历库"""
    await repository_service.delete_repository(db, repository_id)
    return {"message": "删除成功"}


@router.post("/bulk-delete")
async def bulk_delete_repositories(
    repository_ids: List[int],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """批量删除简历库"""
    for repository_id in repository_ids:
        await repository_service.delete_repository(db, repository_id)
    return {"message": "批量删除成功"}


@router.get("/{repository_id}/detail")
async def get_repository_detail(
    repository_id: int,
    list_only: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历库详情"""
    return await repository_service.get_repository_detail(
        db,
        repository_id,
        list_only
    ) 
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services import repository_service

router = APIRouter()


@router.get("", response_model=schemas.ResumeRepositoryListResponse)
def read_repositories(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历库列表"""
    skip = (page - 1) * per_page
    
    if current_user.is_superuser:
        repositories = crud.repository.get_multi(db, skip=skip, limit=per_page)
        total = crud.repository.count(db)
    else:
        repositories = crud.repository.get_multi_by_tenant(
            db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=per_page
        )
        total = crud.repository.count_by_tenant(
            db, 
            tenant_id=current_user.tenant_id
        )
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": repositories,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "",
    response_model=schemas.ResumeRepository,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["repository_create"]
            )
        )
    ]
)
async def create_repository(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Body(...),
    resume_type: str = Body(...),
    description: str = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新简历库"""
    # 检查同名简历库
    if crud.repository.get_by_name(db, name=name):
        raise HTTPException(
            status_code=400,
            detail="该简历库名称已存在"
        )
    
    return await repository_service.create_repository(
        db,
        name=name,
        resume_type=resume_type,
        description=description,
        tenant_id=current_user.tenant_id
    )


@router.get(
    "/statistics",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["repository_read"]
            )
        )
    ]
)
async def get_repository_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历库统计信息"""
    if current_user.is_superuser:
        return await repository_service.get_repository_stats(db)
    else:
        return await repository_service.get_repository_stats_by_tenant(
            db,
            tenant_id=current_user.tenant_id
        )


@router.get(
    "/{repository_id}/detail",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["repository_read"]
            )
        )
    ]
)
async def get_repository_detail(
    repository_id: int,
    list_only: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历库详情"""
    repository = crud.repository.get(db, id=repository_id)
    if not repository:
        raise HTTPException(status_code=404, detail="简历库不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and repository.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该简历库")
    
    return await repository_service.get_repository_detail(
        db,
        repository_id,
        list_only
    )


@router.delete(
    "/{repository_id}",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["repository_delete"]
            )
        )
    ]
)
async def delete_repository(
    repository_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除指定的简历库"""
    repository = crud.repository.get(db, id=repository_id)
    if not repository:
        raise HTTPException(status_code=404, detail="简历库不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and repository.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该简历库")
    
    # 检查是否有关联的简历
    resumes = crud.resume.get_by_repository(db, repository_id=repository_id)
    if resumes:
        raise HTTPException(
            status_code=400,
            detail="该简历库下存在简历,无法删除"
        )
    
    await repository_service.delete_repository(db, repository_id)
    return {"message": "删除成功"}


@router.post(
    "/bulk-delete",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["repository_delete"]
            )
        )
    ]
)
async def bulk_delete_repositories(
    repository_ids: List[int],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """批量删除简历库"""
    for repository_id in repository_ids:
        repository = crud.repository.get(db, id=repository_id)
        if not repository:
            continue
            
        # 检查租户权限
        if not current_user.is_superuser and repository.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail=f"无权删除简历库 {repository_id}")
            
        # 检查是否有关联的简历
        resumes = crud.resume.get_by_repository(db, repository_id=repository_id)
        if resumes:
            raise HTTPException(
                status_code=400,
                detail=f"简历库 {repository_id} 下存在简历,无法删除"
            )
            
        await repository_service.delete_repository(db, repository_id)
        
    return {"message": "批量删除成功"} 
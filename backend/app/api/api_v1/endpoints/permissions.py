from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.PermissionListResponse)
def read_permissions(
    db: Session = Depends(deps.get_db),
    page: int = 1,
    per_page: int = 100
) -> Any:
    """获取所有权限列表"""
    skip = (page - 1) * per_page
    permissions = crud.permission.get_multi(db, skip=skip, limit=per_page)
    total = crud.permission.count(db)
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": permissions,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "/",
    response_model=schemas.Permission,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_in: schemas.PermissionCreate,
) -> Any:
    """创建新权限"""
    permission = crud.permission.get_by_name(db, name=permission_in.name)
    if permission:
        raise HTTPException(
            status_code=400,
            detail="该权限已存在"
        )
    permission = crud.permission.create(db=db, obj_in=permission_in)
    return permission


@router.get(
    "/{permission_id}",
    response_model=schemas.Permission,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def read_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
) -> Any:
    """获取指定权限信息"""
    permission = crud.permission.get(db=db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission


@router.put(
    "/{permission_id}",
    response_model=schemas.Permission,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def update_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
    permission_in: schemas.PermissionUpdate,
) -> Any:
    """更新权限信息"""
    permission = crud.permission.get(db=db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    permission = crud.permission.update(
        db=db,
        db_obj=permission,
        obj_in=permission_in
    )
    return permission


@router.delete(
    "/{permission_id}",
    response_model=schemas.Permission,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def delete_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
) -> Any:
    """删除权限"""
    permission = crud.permission.get(db=db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    permission = crud.permission.remove(db=db, id=permission_id)
    return permission


@router.get("/me", response_model=List[str])
def get_my_permissions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """
    获取当前登录用户的权限集合
    返回权限标识符列表
    """
    permissions = set()
    for role in current_user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    
    return list(permissions) 
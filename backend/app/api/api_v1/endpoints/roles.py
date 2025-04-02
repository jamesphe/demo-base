from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.RoleListResponse)
def read_roles(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
) -> Any:
    """获取角色列表"""
    skip = (page - 1) * per_page
    roles = crud.role.get_multi(db, skip=skip, limit=per_page)
    total = crud.role.count(db)
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": roles,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "/", 
    response_model=schemas.Role,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["role_create"]
            )
        )
    ]
)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
) -> Any:
    """创建新角色"""
    role = crud.role.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="该角色名已存在"
        )
    role = crud.role.create(db=db, obj_in=role_in)
    return role


@router.put(
    "/{role_id}/permissions",
    response_model=schemas.Role,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["role_update"]
            )
        )
    ]
)
def update_role_permissions(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    permission_ids: List[int],
) -> Any:
    """更新角色权限"""
    role = crud.role.get(db=db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    
    permissions = []
    for perm_id in permission_ids:
        perm = crud.permission.get(db=db, id=perm_id)
        if perm:
            permissions.append(perm)
    
    role.permissions = permissions
    db.add(role)
    db.commit()
    db.refresh(role)
    return role 
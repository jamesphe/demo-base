from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.tenant_service import tenant_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.Tenant],
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def read_tenants(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """获取租户列表"""
    tenants = crud.tenant.get_multi(db, skip=skip, limit=limit)
    return tenants


@router.post(
    "/",
    response_model=schemas.Tenant,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def create_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_in: schemas.TenantCreate,
) -> Any:
    """创建新租户"""
    tenant = tenant_service.create_tenant(db=db, tenant_in=tenant_in)
    return tenant


@router.get(
    "/{tenant_id}",
    response_model=schemas.Tenant,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def read_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
) -> Any:
    """获取指定租户信息"""
    tenant = crud.tenant.get(db=db, id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    return tenant


@router.put(
    "/{tenant_id}",
    response_model=schemas.Tenant,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def update_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    tenant_in: schemas.TenantUpdate,
) -> Any:
    """更新租户信息"""
    tenant = crud.tenant.get(db=db, id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    tenant = tenant_service.update_tenant(
        db=db,
        tenant=tenant,
        tenant_in=tenant_in
    )
    return tenant


@router.delete(
    "/{tenant_id}",
    response_model=schemas.Tenant,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def delete_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
) -> Any:
    """删除租户"""
    tenant = crud.tenant.get(db=db, id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    tenant = crud.tenant.remove(db=db, id=tenant_id)
    return tenant 
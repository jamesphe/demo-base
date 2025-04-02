from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.services.tenant_service import tenant_service


router = APIRouter()


@router.get(
    "/",
    response_model=schemas.TenantListResponse,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
def read_tenants(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
) -> Any:
    """获取租户列表"""
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    tenants = crud.tenant.get_multi(db, skip=skip, limit=per_page)
    total = crud.tenant.count(db)
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": tenants,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


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
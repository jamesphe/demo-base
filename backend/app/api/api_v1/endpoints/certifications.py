from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.services.certification_service import certification_service

router = APIRouter()


@router.get("/", response_model=schemas.CertificationListResponse)
def read_certifications(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    tenant_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    name: Optional[str] = None,
    issuing_organization: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取证书列表"""
    skip = (page - 1) * per_page
    
    # 构建过滤条件
    filters = {}
    if status:
        filters["status"] = status
    if category:
        filters["category"] = category
    if name:
        filters["name"] = name
    if issuing_organization:
        filters["issuing_organization"] = issuing_organization
    
    # 如果用户不是超级管理员，则只能查看自己租户的证书
    if not current_user.is_superuser:
        tenant_id = current_user.tenant_id
    
    certifications = certification_service.get_certifications(
        db=db, 
        tenant_id=tenant_id, 
        skip=skip, 
        limit=per_page, 
        filters=filters
    )
    total = certification_service.count_certifications(
        db=db,
        tenant_id=tenant_id,
        filters=filters
    )
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": certifications,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post("/", response_model=schemas.certification.Certification)
def create_certification(
    *,
    db: Session = Depends(deps.get_db),
    certification_in: schemas.certification.CertificationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新证书。
    """
    # 如果用户不是超级管理员，则只能为自己的租户创建证书
    if not current_user.is_superuser:
        certification_in.tenant_id = current_user.tenant_id
    
    certification = certification_service.create_certification(
        db=db, certification_in=certification_in
    )
    return certification


@router.get(
    "/{certification_id}", 
    response_model=schemas.certification.Certification
)
def read_certification(
    *,
    db: Session = Depends(deps.get_db),
    certification_id: int = Path(..., title="要获取的证书ID"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取特定证书的详细信息。
    """
    certification = certification_service.get_certification(
        db=db, certification_id=certification_id
    )
    if not certification:
        raise HTTPException(status_code=404, detail="证书不存在")
    
    # 检查权限：超级管理员可以查看所有证书，普通用户只能查看自己租户的证书或公共证书
    if (not current_user.is_superuser and 
            certification.tenant_id not in [None, current_user.tenant_id]):
        raise HTTPException(status_code=403, detail="没有权限访问此证书")
    
    return certification


@router.put(
    "/{certification_id}", 
    response_model=schemas.certification.Certification
)
def update_certification(
    *,
    db: Session = Depends(deps.get_db),
    certification_id: int = Path(..., title="要更新的证书ID"),
    certification_in: schemas.certification.CertificationUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新证书信息。
    """
    certification = certification_service.get_certification(
        db=db, certification_id=certification_id
    )
    if not certification:
        raise HTTPException(status_code=404, detail="证书不存在")
    
    # 检查权限：超级管理员可以更新所有证书，普通用户只能更新自己租户的证书
    if (not current_user.is_superuser and 
            certification.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=403, detail="没有权限更新此证书")
    
    # 如果用户不是超级管理员，不允许更改租户ID
    if (not current_user.is_superuser and 
            certification_in.tenant_id is not None):
        certification_in.tenant_id = current_user.tenant_id
    
    certification = certification_service.update_certification(
        db=db, certification=certification, certification_in=certification_in
    )
    return certification


@router.delete(
    "/{certification_id}", 
    response_model=schemas.certification.Certification
)
def delete_certification(
    *,
    db: Session = Depends(deps.get_db),
    certification_id: int = Path(..., title="要删除的证书ID"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    软删除证书（将状态设置为inactive）。
    """
    certification = certification_service.get_certification(
        db=db, certification_id=certification_id
    )
    if not certification:
        raise HTTPException(status_code=404, detail="证书不存在")
    
    # 检查权限：超级管理员可以删除所有证书，普通用户只能删除自己租户的证书
    if (not current_user.is_superuser and 
            certification.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=403, detail="没有权限删除此证书")
    
    certification = certification_service.delete_certification(
        db=db, certification=certification
    )
    return certification 
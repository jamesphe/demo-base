from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services import resume_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.Resume],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_review_read"]
            )
        )
    ]
)
def get_pending_reviews(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取待审核的简历列表"""
    if current_user.is_superuser:
        resumes = crud.resume.get_by_review_status(
            db, status="pending", skip=skip, limit=limit
        )
    else:
        resumes = crud.resume.get_by_review_status_and_tenant(
            db, 
            status="pending", 
            tenant_id=current_user.tenant_id,
            skip=skip, 
            limit=limit
        )
    return resumes


@router.post(
    "/{resume_id}/approve",
    response_model=schemas.Resume,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_review_update"]
            )
        )
    ]
)
def approve_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    comment: str = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """审核通过简历"""
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权审核该简历")
    
    return resume_service.approve_resume(
        db=db,
        resume_id=resume_id,
        reviewer_id=current_user.id,
        comment=comment
    )


@router.post(
    "/{resume_id}/reject",
    response_model=schemas.Resume,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_review_update"]
            )
        )
    ]
)
def reject_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    comment: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """拒绝简历"""
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权审核该简历")
    
    return resume_service.reject_resume(
        db=db,
        resume_id=resume_id,
        reviewer_id=current_user.id,
        comment=comment
    ) 
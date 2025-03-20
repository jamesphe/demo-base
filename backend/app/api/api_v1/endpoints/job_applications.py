from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post(
    "/jobs/{job_id}/apply",
    response_model=schemas.JobApplication,
    dependencies=[Depends(deps.get_current_active_user)]
)
def apply_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    application_in: schemas.JobApplicationCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """申请职位"""
    # 检查职位是否存在且状态为已发布
    job = crud.job.get(db, id=job_id)
    if not job or job.status != "published":
        raise HTTPException(
            status_code=404,
            detail="职位不存在或未发布"
        )
    
    # 检查是否已经申请过
    existing_application = db.query(models.JobApplication).filter(
        models.JobApplication.job_id == job_id,
        models.JobApplication.resume_id == application_in.resume_id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="已经申请过该职位"
        )
    
    application = crud.job_application.create(
        db,
        obj_in=application_in
    )
    return application


@router.put(
    "/applications/{application_id}",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_review"]
            )
        )
    ]
)
def update_application_status(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    status_update: schemas.JobApplicationUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """更新申请状态"""
    application = crud.job_application.get(db, id=application_id)
    if not application:
        raise HTTPException(
            status_code=404,
            detail="申请记录不存在"
        )
    
    # 检查权限
    job = crud.job.get(db, id=application.job_id)
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="无权更新该申请状态"
        )
    
    application = crud.job_application.update_status(
        db,
        application_id=application_id,
        status=status_update.status,
        review_notes=status_update.review_notes
    )
    return application 
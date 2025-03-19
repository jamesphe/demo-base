from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import crud, models, schemas
from app.api import deps
from app.services.job_service import JobService

router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.JobWithCandidateCount],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_read"]
            )
        )
    ]
)
def read_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取职位列表"""
    service = JobService(db)
    if current_user.is_superuser:
        jobs = service.list_jobs(skip=skip, limit=limit)
    else:
        jobs = service.list_jobs(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit
        )
    return jobs


@router.post(
    "/",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_create"]
            )
        )
    ]
)
def create_job(
    *,
    db: Session = Depends(deps.get_db),
    job_in: schemas.JobCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新职位"""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="当前用户未关联租户，无法创建职位"
        )
    
    service = JobService(db)
    job = service.create_job(
        job_in=job_in,
        tenant_id=current_user.tenant_id,
        publisher_id=current_user.id
    )
    return job


@router.get(
    "/{job_id}",
    response_model=schemas.JobWithCandidateCount,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_read"]
            )
        )
    ]
)
def read_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取指定职位信息"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该职位信息")
    
    return job


@router.put(
    "/{job_id}",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_update"]
            )
        )
    ]
)
def update_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    job_in: schemas.JobUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """更新职位信息"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该职位")
    
    job = service.update_job(job_id=job_id, job_in=job_in)
    return job


@router.post(
    "/{job_id}/publish",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_update"]
            )
        )
    ]
)
def publish_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """发布职位"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权发布该职位")

    job = service.publish_job(job_id)
    return job


@router.post(
    "/{job_id}/close",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_update"]
            )
        )
    ]
)
def close_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """关闭职位"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权关闭该职位")

    job = service.close_job(job_id)
    return job


@router.delete(
    "/{job_id}",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_delete"]
            )
        )
    ]
)
def delete_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除职位"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该职位")
    
    # 检查是否有关联的候选人
    if job.candidates:
        raise HTTPException(
            status_code=400,
            detail="该职位下存在候选人,无法删除"
        )
    
    service.delete_job(job_id)
    return job


@router.get(
    "/{job_id}/candidates",
    response_model=List[schemas.CandidateWithInterviews],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_read", "candidate_read"]
            )
        )
    ]
)
def read_job_candidates(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取职位下的候选人列表"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该职位的候选人信息")
    
    candidates = crud.candidate.get_by_job(db, job_id=job_id)
    return candidates 
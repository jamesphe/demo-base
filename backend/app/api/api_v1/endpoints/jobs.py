from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import crud, models, schemas
from app.api import deps
from app.services.job_service import job_service

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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取职位列表"""
    return job_service.list_jobs(
        db=db,
        skip=skip,
        limit=limit,
        tenant_id=current_tenant_id
    )


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
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user_id: int = Depends(deps.get_current_user_id)
) -> Any:
    """创建新职位"""
    return job_service.create_job(
        db=db,
        job_in=job_in,
        tenant_id=current_tenant_id,
        publisher_id=current_user_id
    )


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
) -> Any:
    """获取指定职位信息"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新职位信息"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job_service.update_job(
        db=db,
        job_id=job_id,
        job_in=job_in,
        tenant_id=current_tenant_id
    )


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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """发布职位"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    return job_service.publish_job(
        db=db,
        job_id=job_id,
        tenant_id=current_tenant_id
    )


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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """关闭职位"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    return job_service.close_job(
        db=db,
        job_id=job_id,
        tenant_id=current_tenant_id
    )


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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """删除职位"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查是否有关联的候选人
    if job.candidates:
        raise HTTPException(
            status_code=400,
            detail="该职位下存在候选人,无法删除"
        )
    
    return job_service.delete_job(
        db=db,
        job_id=job_id,
        tenant_id=current_tenant_id
    )


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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取职位下的候选人列表"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    candidates = crud.candidate.get_by_job(db, job_id=job_id)
    return candidates


@router.post(
    "/{job_id}/skills",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_update"]
            )
        )
    ]
)
def update_job_skills(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    skills: List[schemas.JobRequiredSkill],
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新职位所需技能"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job_service.update_job_skills(
        db=db,
        job_id=job_id,
        skills=skills,
        tenant_id=current_tenant_id
    )


@router.post(
    "/{job_id}/certifications",
    response_model=schemas.Job,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_update"]
            )
        )
    ]
)
def update_job_certifications(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    certifications: List[schemas.JobRequiredCertification],
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新职位所需证书"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job_service.update_job_certifications(
        db=db,
        job_id=job_id,
        certifications=certifications,
        tenant_id=current_tenant_id
    )


@router.get(
    "/{job_id}/skills",
    response_model=List[schemas.JobRequiredSkill],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_read"]
            )
        )
    ]
)
def read_job_skills(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
) -> Any:
    """获取职位所需技能列表"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job.required_skills


@router.get(
    "/{job_id}/certifications",
    response_model=List[schemas.JobRequiredCertification],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_read"]
            )
        )
    ]
)
def read_job_certifications(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
) -> Any:
    """获取职位所需证书列表"""
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    return job.required_certifications 
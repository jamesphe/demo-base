from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.get("/external/{external_id}", response_model=schemas.Job)
def read_job_by_external_id(
    external_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    通过外部 ID 获取职位信息
    """
    job = job_service.get_job_by_external_id(db, external_id=external_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # 权限检查
    if (not crud.user.is_superuser(current_user) and 
            job.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return job


@router.post(
    "/{job_id}/applications",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_create"]
            )
        )
    ]
)
def create_job_application(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    application_in: schemas.JobApplicationCreate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user_id: int = Depends(deps.get_current_user_id)
) -> Any:
    """创建职位申请"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application_in.job_id != job_id:
        raise HTTPException(status_code=400, detail="职位ID不匹配")
    
    # 检查简历是否存在
    resume = crud.resume.get(db=db, id=application_in.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查是否已经申请过该职位
    existing_application = crud.job_application.get_by_job_and_resume(
        db=db, 
        job_id=job_id, 
        resume_id=application_in.resume_id
    )
    if existing_application:
        raise HTTPException(
            status_code=400, 
            detail="已经申请过该职位"
        )
    
    return crud.job_application.create_with_owner(
        db=db,
        obj_in=application_in,
        tenant_id=current_tenant_id,
        created_by=current_user_id
    )


@router.get(
    "/{job_id}/applications",
    response_model=List[schemas.JobApplication],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_job_applications(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取指定职位的所有申请"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    if job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限访问此职位的申请")
    
    return crud.job_application.get_by_job(db=db, job_id=job_id)


@router.get(
    "/{job_id}/applications/{application_id}",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_job_application(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    application_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取指定职位申请信息"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application.job_id != job_id:
        raise HTTPException(status_code=404, detail="职位申请不存在于该职位下")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限访问此职位申请")
    
    return application


@router.put(
    "/{job_id}/applications/{application_id}",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_update"]
            )
        )
    ]
)
def update_job_application(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    application_id: int,
    application_in: schemas.JobApplicationUpdate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新职位申请状态"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application.job_id != job_id:
        raise HTTPException(status_code=404, detail="职位申请不存在于该职位下")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限更新此职位申请")
    
    return crud.job_application.update(
        db=db,
        db_obj=application,
        obj_in=application_in
    )


@router.delete(
    "/{job_id}/applications/{application_id}",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_delete"]
            )
        )
    ]
)
def delete_job_application(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    application_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """删除职位申请"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application.job_id != job_id:
        raise HTTPException(status_code=404, detail="职位申请不存在于该职位下")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限删除此职位申请")
    
    return crud.job_application.remove(db=db, id=application_id)

# ... 可能需要添加其他使用 external_id 的端点 ... 
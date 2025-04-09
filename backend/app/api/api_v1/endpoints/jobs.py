from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.job_service import job_service
from app.services.job_application_service import job_application_service

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.JobListResponse,
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
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    departmentId: Optional[int] = None,
    createTime: Optional[List[str]] = Query(None),
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取职位列表
    
    Args:
        page: 当前页码，从1开始
        per_page: 每页数量
        keyword: 职位名称关键词
        status: 职位状态(0-关闭 1-开启)
        departmentId: 部门ID
        createTime: 创建时间范围，格式["2024-01-01", "2024-03-20"]
    """
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 构建查询条件
    filters = {
        "tenant_id": current_tenant_id
    }
    
    if keyword:
        filters["title"] = {"like": f"%{keyword}%"}
    if status is not None:
        filters["status"] = status
    if departmentId:
        filters["department_id"] = departmentId
    if createTime and len(createTime) == 2:
        filters["create_time"] = {
            "between": createTime
        }
        
    # 获取数据和总数
    jobs, total = job_service.list_jobs_with_count(
        db=db,
        skip=skip,
        limit=per_page,
        tenant_id=current_tenant_id,
        filters=filters
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": jobs,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


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
    current_tenant_id: Optional[int] = Depends(deps.get_current_tenant_id),
    current_user_id: int = Depends(deps.get_current_user_id)
) -> Any:
    """创建新职位"""
    if not current_tenant_id:
        raise HTTPException(
            status_code=400,
            detail="当前用户未关联租户，无法创建职位"
        )
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
    current_user_id: int = Depends(deps.get_current_user_id),
    background_tasks: BackgroundTasks
) -> Any:
    """创建职位申请"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application_in.job_id != job_id:
        raise HTTPException(status_code=400, detail="职位ID不匹配")
    
    return job_application_service.create_application_with_validation(
        db=db,
        application_in=application_in,
        tenant_id=current_tenant_id,
        created_by=current_user_id,
        background_tasks=background_tasks
    )


@router.get(
    "/{job_id}/applications",
    response_model=List[schemas.JobApplicationWithResumeInfo],
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
    """获取指定职位的所有申请（包含简历基本信息）"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    if job.tenant_id != current_tenant_id:
        raise HTTPException(
            status_code=403, 
            detail="没有权限访问此职位的申请"
        )
    
    applications = job_application_service.get_applications_by_job_with_resume_info(
        db=db, 
        job_id=job_id
    )
    return applications


@router.get(
    "/{job_id}/applications/{application_id}",
    response_model=schemas.JobApplicationWithResume,
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
    """获取指定职位申请信息（包含完整简历信息）"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    application = job_application_service.get_application_with_resume(
        db=db, application_id=application_id
    )
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
    
    application = job_application_service.get_application(
        db=db, 
        application_id=application_id
    )
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application.job_id != job_id:
        raise HTTPException(status_code=404, detail="职位申请不存在于该职位下")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限更新此职位申请")
    
    return job_application_service.update_application(
        db=db,
        application_id=application_id,
        application_in=application_in
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
    
    application = job_application_service.get_application(
        db=db, application_id=application_id
    )
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 确保申请的职位ID与路径中的ID一致
    if application.job_id != job_id:
        raise HTTPException(status_code=404, detail="职位申请不存在于该职位下")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限删除此职位申请")
    
    return job_application_service.delete_application(
        db=db, application_id=application_id)

# ... 可能需要添加其他使用 external_id 的端点 ... 
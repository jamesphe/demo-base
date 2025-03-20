from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.post(
    "/",
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
    application_in: schemas.JobApplicationCreate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user_id: int = Depends(deps.get_current_user_id)
) -> Any:
    """创建职位申请"""
    # 检查职位是否存在
    job = crud.job.get(db=db, id=application_in.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查简历是否存在
    resume = crud.resume.get(db=db, id=application_in.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查是否已经申请过该职位
    existing_application = crud.job_application.get_by_job_and_resume(
        db=db, 
        job_id=application_in.job_id, 
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
    "/",
    response_model=List[schemas.JobApplication],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_all_job_applications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取所有职位申请列表（跨职位）"""
    return crud.job_application.get_by_tenant(
        db=db,
        tenant_id=current_tenant_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/status/{status}",
    response_model=List[schemas.JobApplication],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_applications_by_status(
    *,
    db: Session = Depends(deps.get_db),
    status: str,
    skip: int = 0,
    limit: int = 100,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取指定状态的所有职位申请"""
    # 验证状态值是否有效
    valid_statuses = ["pending", "reviewed", "interviewed", "offered", "rejected", "withdrawn"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效的状态值，有效值为: {', '.join(valid_statuses)}")
    
    applications = crud.job_application.get_by_status(
        db=db, 
        status=status,
        skip=skip,
        limit=limit
    )
    
    # 过滤当前租户的申请
    return [app for app in applications if app.tenant_id == current_tenant_id]


@router.get(
    "/resume/{resume_id}",
    response_model=List[schemas.JobApplication],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_applications_by_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取指定简历的所有申请"""
    # 检查简历是否存在
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    if resume.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限访问此简历的申请")
    
    return crud.job_application.get_by_resume(db=db, resume_id=resume_id)


@router.get(
    "/{application_id}",
    response_model=schemas.JobApplication,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_job_application_by_id(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """通过ID获取职位申请信息（不需要指定职位ID）"""
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限访问此职位申请")
    
    return application


@router.put(
    "/{application_id}",
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
    application_id: int,
    application_in: schemas.JobApplicationUpdate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新职位申请状态"""
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限更新此职位申请")
    
    return crud.job_application.update(
        db=db,
        db_obj=application,
        obj_in=application_in
    )


@router.delete(
    "/{application_id}",
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
    application_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """删除职位申请"""
    application = crud.job_application.get(db=db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限删除此职位申请")
    
    return crud.job_application.remove(db=db, id=application_id)


@router.get(
    "/job/{job_id}",
    response_model=List[schemas.JobApplication],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_read"]
            )
        )
    ]
)
def read_applications_by_job(
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
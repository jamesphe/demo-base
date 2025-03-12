from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import crud, models, schemas
from app.api import deps

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
    """
    获取职位列表，包含每个职位的候选人数量
    """
    # 查询职位及其候选人数量
    jobs = db.query(
        models.Job,
        func.count(models.Candidate.id).label('candidate_count')
    ).outerjoin(
        models.Candidate
    ).group_by(
        models.Job.id
    ).offset(skip).limit(limit).all()
    
    # 转换为带有候选人数量的职位列表
    result = []
    for job, candidate_count in jobs:
        job_dict = schemas.Job.model_validate(job).model_dump()
        job_dict['candidate_count'] = candidate_count
        result.append(schemas.JobWithCandidateCount(**job_dict))
    
    return result


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
    # 创建职位并关联到当前租户
    job = crud.job.create_with_tenant(
        db=db,
        obj_in=job_in,
        tenant_id=current_user.tenant_id
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
    job = crud.job.get(db=db, id=job_id)
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
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该职位信息")
    
    job = crud.job.update(
        db=db,
        db_obj=job,
        obj_in=job_in
    )
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
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该职位")
    
    # 检查是否有关联的候选人
    candidates = crud.candidate.get_by_job(db, job_id=job_id)
    if candidates:
        raise HTTPException(
            status_code=400,
            detail="该职位下存在候选人,无法删除"
        )
    
    job = crud.job.remove(db=db, id=job_id)
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
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该职位的候选人信息")
    
    candidates = crud.candidate.get_by_job(db, job_id=job_id)
    return candidates 
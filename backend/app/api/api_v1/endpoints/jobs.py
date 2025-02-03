from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Job])
def read_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取职位列表
    """
    jobs = crud.job.get_multi(db, skip=skip, limit=limit)
    return jobs


@router.post("/", response_model=schemas.Job)
def create_job(
    *,
    db: Session = Depends(deps.get_db),
    job_in: schemas.JobCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新职位
    """
    job = crud.job.create(db=db, obj_in=job_in)
    return job


@router.put("/{job_id}", response_model=schemas.Job)
def update_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    job_in: schemas.JobUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新职位信息
    """
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    job = crud.job.update(db=db, db_obj=job, obj_in=job_in)
    return job


@router.get("/{job_id}", response_model=schemas.Job)
def read_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取指定职位信息
    """
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return job


@router.delete("/{job_id}", response_model=schemas.Job)
def delete_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除职位
    """
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    job = crud.job.remove(db=db, id=job_id)
    return job 
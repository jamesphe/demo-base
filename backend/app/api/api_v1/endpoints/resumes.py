import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from datetime import datetime
import uuid
import aiofiles
from app.services import resume_service

router = APIRouter()

def validate_file_extension(filename: str) -> bool:
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    return filename.split(".")[-1].lower() in allowed_extensions

@router.post(
    "/upload",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_create"]
            )
        )
    ]
)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    repository_name: str = Form(...),
    resume_type: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """批量上传简历文件到指定简历库"""
    # 验证文件类型
    for file in files:
        if not resume_service.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
    
    # 创建或获取简历库
    repository = await resume_service.get_or_create_repository(
        db,
        name=repository_name,
        resume_type=resume_type,
        description=description,
        tenant_id=current_user.tenant_id
    )
    
    # 异步处理文件上传和解析
    for file in files:
        background_tasks.add_task(
            resume_service.process_resume_file,
            db,
            file,
            repository.id,
            current_user.tenant_id
        )
    
    return {"message": "简历上传成功,正在处理中"}

@router.get(
    "/",
    response_model=List[schemas.Resume],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read"]
            )
        )
    ]
)
def read_resumes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历列表"""
    if current_user.is_superuser:
        resumes = crud.resume.get_multi(db, skip=skip, limit=limit)
    else:
        resumes = crud.resume.get_multi_by_tenant(
            db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit
        )
    return resumes

@router.get(
    "/{resume_id}",
    response_model=schemas.Resume,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read"]
            )
        )
    ]
)
def read_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取简历详情"""
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该简历")
    
    return resume

@router.get(
    "/candidate/{candidate_id}",
    response_model=List[schemas.Resume],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read", "candidate_read"]
            )
        )
    ]
)
def get_candidate_resumes(
    *,
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取候选人的所有简历"""
    # 验证候选人是否存在
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该候选人的简历")
    
    resumes = crud.resume.get_by_candidate(db=db, candidate_id=candidate_id)
    return resumes

@router.post(
    "/parse",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_parse"]
            )
        )
    ]
)
async def parse_resume(
    *,
    file_url: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """解析简历内容"""
    # 验证文件权限
    resume = crud.resume.get_by_file_url(db, file_url=file_url)
    if resume and not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权解析该简历")
    
    parsed_data = await resume_service.parse_resume(file_url)
    return {"parsed_data": parsed_data}

@router.delete(
    "/{resume_id}",
    response_model=schemas.Resume,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_delete"]
            )
        )
    ]
)
def delete_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """删除简历"""
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and resume.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该简历")
    
    # 删除关联的文件
    resume_service.delete_resume_file(resume.file_path)
    
    resume = crud.resume.remove(db=db, id=resume_id)
    return resume 
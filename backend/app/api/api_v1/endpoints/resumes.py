from typing import Any, List, Optional
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, 
    File, Form, BackgroundTasks, Query, Path
)
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.core.config import settings
from app.services import resume_service
from app.services import job_service
from app.services import job_application_service
import time
import random


router = APIRouter()


def validate_file_extension(filename: str) -> bool:
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    return filename.split(".")[-1].lower() in allowed_extensions


@router.post(
    "/upload",
    response_model=schemas.ResponseMsg,
    summary="上传简历文件",
    description="上传简历文件进行解析,可选择关联到简历库和职位",
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
    file: UploadFile = File(...),
    repository_name: Optional[str] = Form(None),
    resume_type: Optional[str] = Form("general"),  # 默认为通用简历
    description: Optional[str] = Form(None),
    job_id: Optional[int] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """上传简历文件进行解析"""
    # 验证文件类型
    if not resume_service.validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.filename}"
        )
    
    repository_id = None
    # 只有当提供了repository_name时才创建或获取简历库
    if repository_name:
        repository = await resume_service.get_or_create_repository(
            db,
            name=repository_name,
            resume_type=resume_type,
            description=description,
            tenant_id=current_user.tenant_id
        )
        repository_id = repository.id
    
    # 验证职位ID(如果提供)
    if job_id:
        job = job_service.get_job(db=db, job_id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
        if (not current_user.is_superuser and 
                job.tenant_id != current_user.tenant_id):
            raise HTTPException(status_code=403, detail="无权访问该职位")
    
    # 添加后台任务处理简历
    background_tasks.add_task(
        resume_service.process_resume_file,
        db,
        file,
        repository_id,
        current_user,
        job_id,
        background_tasks
    )
    
    return {"message": "简历上传成功，正在处理中"}


@router.get(
    "/",
    response_model=schemas.ResumeList,
    summary="获取简历列表",
    description="分页获取简历列表，支持按条件筛选",
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
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="姓名"),
    processing_status: Optional[str] = Query(None, description="处理状态"),
    resume_type: Optional[str] = Query(None, description="简历类型"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历列表"""
    skip = (page - 1) * limit
    
    # 构建过滤条件
    filters = {}
    if name:
        filters["name"] = name
    if processing_status:
        filters["processing_status"] = processing_status
    if resume_type:
        filters["resume_type"] = resume_type
    
    # 获取简历列表
    resumes = resume_service.get_resumes_with_filters(
        db=db,
        tenant_id=(
            current_user.tenant_id if not current_user.is_superuser else None
        ),
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    # 获取总数
    total = resume_service.get_resumes_count_with_filters(
        db=db,
        tenant_id=(
            current_user.tenant_id if not current_user.is_superuser else None
        ),
        filters=filters
    )
    
    # 返回与 ResumeList 模型匹配的结构
    return {
        "items": resumes,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get(
    "/{resume_id}",
    response_model=schemas.Resume,
    summary="获取简历详情",
    description="根据简历ID获取简历详细信息",
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
    resume_id: int = Path(..., description="简历ID"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取简历详情"""
    resume = resume_service.get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权访问该简历"
        )
    
    return resume


@router.get(
    "/candidate/{candidate_id}",
    response_model=List[schemas.Resume],
    summary="获取候选人简历",
    description="获取指定候选人的所有简历",
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
    candidate_id: int = Path(..., description="候选人ID"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取候选人的所有简历"""
    # 验证候选人是否存在
    candidate = resume_service.get_candidate(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            candidate.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权访问该候选人的简历"
        )
    
    resumes = resume_service.get_resumes_by_candidate(
        db=db, 
        candidate_id=candidate_id
    )
    return resumes


@router.post(
    "/parse",
    response_model=schemas.ResumeParseResponse,
    summary="解析简历",
    description="解析指定URL的简历文件内容",
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
    file_url: str = Query(..., description="文件URL"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """解析简历内容"""
    # 验证文件权限
    resume = resume_service.get_resume_by_file_url(db, file_url=file_url)
    if (resume and not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权解析该简历"
        )
    
    parsed_data = await resume_service.parse_resume(file_url)
    return {"parsed_data": parsed_data}


@router.put(
    "/{resume_id}",
    response_model=schemas.Resume,
    summary="更新简历",
    description="更新指定简历的信息",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_update"]
            )
        )
    ]
)
def update_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int = Path(..., description="简历ID"),
    resume_in: schemas.ResumeUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """更新简历信息"""
    resume = resume_service.get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权更新该简历"
        )
    
    # 如果是审核操作，记录审核人信息
    if (resume_in.review_status and 
            resume_in.review_status != resume.review_status):
        resume_in.reviewer_id = current_user.id
    
    # 直接传递 resume_in 对象，而不是转换为字典
    updated_resume = resume_service.update_resume(
        db=db, 
        resume=resume, 
        resume_data=resume_in
    )
    return updated_resume


@router.delete(
    "/{resume_id}",
    response_model=schemas.Resume,
    summary="删除简历",
    description="删除指定的简历",
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
    resume_id: int = Path(..., description="简历ID"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """删除简历"""
    resume = resume_service.get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权删除该简历"
        )
    
    # 删除关联的文件
    resume_service.delete_resume_file(resume.file_path)
    
    resume = resume_service.delete_resume(db=db, resume_id=resume_id)
    return resume


@router.post(
    "/",
    response_model=schemas.Resume,
    summary="创建简历",
    description="直接创建完整的简历信息，无需先上传文件，可以不属于任何简历库",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_create"]
            )
        )
    ]
)
async def create_resume(
    *,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    resume_in: schemas.ResumeCreate,
    job_id: Optional[int] = Query(None, description="职位ID"),
    job_external_id: Optional[str] = Query(None, description="职位外部ID"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """创建完整的简历信息"""
    try:
        resume = resume_service.create_resume_with_job(
            db=db,
            resume_data=resume_in.model_dump(),
            current_user=current_user,
            job_id=job_id,
            job_external_id=job_external_id,
            background_tasks=background_tasks
        )
        return resume
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
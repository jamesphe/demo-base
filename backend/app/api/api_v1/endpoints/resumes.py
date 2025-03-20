from typing import Any, List, Optional
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, 
    File, Form, BackgroundTasks, Query, Path
)
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.services import resume_service
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
    description="上传简历文件到指定简历库，并提交简历表单数据",
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
    repository_name: str = Form(...),
    resume_type: str = Form(...),
    description: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    highest_education: Optional[str] = Form(None),
    highest_degree: Optional[str] = Form(None),
    major: Optional[str] = Form(None),
    graduate_school: Optional[str] = Form(None),
    expected_position: Optional[str] = Form(None),
    expected_salary: Optional[str] = Form(None),
    expected_location: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """上传简历文件到指定简历库，并提交简历表单数据"""
    # 验证文件类型
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
    
    # 收集表单数据
    form_data = {
        "name": name,
        "gender": gender,
        "phone": phone,
        "email": email,
        "highest_education": highest_education,
        "highest_degree": highest_degree,
        "major": major,
        "graduate_school": graduate_school,
        "expected_position": expected_position,
        "expected_salary": expected_salary,
        "expected_location": expected_location,
    }
    
    # 过滤掉None值
    form_data = {k: v for k, v in form_data.items() if v is not None}
    
    # 异步处理文件上传和解析
    background_tasks.add_task(
        resume_service.process_resume_file_with_form_data,
        db,
        file,
        repository.id,
        current_user.tenant_id,
        current_user.id,
        current_user.user_type,
        current_user.username,
        form_data
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
    resumes = crud.resume.get_multi_with_filters(
        db=db,
        tenant_id=current_user.tenant_id if not current_user.is_superuser else None,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    # 获取总数
    total = crud.resume.get_multi_with_filters_count(
        db=db,
        tenant_id=current_user.tenant_id if not current_user.is_superuser else None,
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
    resume = crud.resume.get(db=db, id=resume_id)
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
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            candidate.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权访问该候选人的简历"
        )
    
    resumes = crud.resume.get_by_candidate(db=db, candidate_id=candidate_id)
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
    resume = crud.resume.get_by_file_url(db, file_url=file_url)
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
    resume = crud.resume.get(db=db, id=resume_id)
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
    if resume_in.review_status and resume_in.review_status != resume.review_status:
        resume_in.reviewer_id = current_user.id
    
    updated_resume = crud.resume.update(db=db, db_obj=resume, obj_in=resume_in)
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
    resume = crud.resume.get(db=db, id=resume_id)
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
    
    resume = crud.resume.remove(db=db, id=resume_id)
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
def create_resume(
    *,
    db: Session = Depends(deps.get_db),
    resume_in: schemas.ResumeCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """创建完整的简历信息"""
    # 设置发布者信息
    resume_data = resume_in.model_dump()
    resume_data.update({
        "publisher_id": current_user.id,
        "publisher_type": current_user.user_type,
        "publisher_name": current_user.username,
        "tenant_id": current_user.tenant_id
    })
    
    # 验证简历数据
    is_valid, error_message = resume_service.validate_resume_data(resume_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # 生成唯一的简历ID
    if not resume_data.get("resume_id"):
        resume_data["resume_id"] = f"R{int(time.time())}{random.randint(1000, 9999)}"
    
    # 设置手动创建标志
    if not resume_data.get("file_path"):
        resume_data["is_manual_entry"] = True
    
    # 验证简历库权限（如果指定了简历库）
    if resume_data.get("repository_id"):
        repository = crud.repository.get(db, id=resume_data["repository_id"])
        if not repository:
            raise HTTPException(status_code=404, detail="简历库不存在")
        
        if not current_user.is_superuser and repository.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="无权访问该简历库")
    
    # 创建简历
    try:
        # 直接使用字典创建简历
        resume = crud.resume.create(db=db, obj_in=resume_data)
        return resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建简历失败: {str(e)}") 
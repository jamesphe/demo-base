from typing import Any, List, Optional, Dict
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, 
    File, Form, BackgroundTasks, Query, Path
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import case, or_, text
from app import models
from app.api import deps
from app.core.config import settings
from app.services.resume_service import resume_service
from app.services.job_service import job_service
from app.schemas.common import ResponseMsg, ResumeParseResponse
from app.schemas.resume import (
    Resume,
    ResumeListResponse,
    ResumeCreate,
    ResumeUpdate
)
from pydantic import BaseModel
import os
from datetime import datetime
from app.services.job_application_service import job_application_service
from app.services.resume_queue_service import process_resume_task


# 定义请求和响应模型
class AIAnalysisRequest(BaseModel):
    """简历AI解读请求模型"""
    job_requirements: str = ""
    dimensions: List[str] = ["技能匹配度", "专业经验", "教育背景", "职业发展", "综合能力"]
    questions: Optional[str] = None
    include_interview_tips: bool = True


class SkillMatch(BaseModel):
    """技能匹配模型"""
    name: str
    match: int


class AIAnalysisResponse(BaseModel):
    """简历AI解读响应模型"""
    summary: str
    match_score: int
    skill_analysis: str
    skills: List[SkillMatch]
    experience_analysis: str
    education_analysis: str
    career_analysis: str
    strengths: List[str]
    weaknesses: List[str]
    interview_tips: Optional[str] = None
    suggested_questions: Optional[List[str]] = None
    conclusion: str
    recommendation: str


router = APIRouter()


def validate_file_extension(filename: str) -> bool:
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    return filename.split(".")[-1].lower() in allowed_extensions


@router.get(
    "/search",
    response_model=ResumeListResponse,
    summary="搜索简历",
    description="根据关键词和其他条件搜索简历",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read"]
            )
        )
    ]
)
def search_resumes(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(12, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    experience: Optional[str] = Query(None, description="工作经验"),
    education: Optional[str] = Query(None, description="教育背景"),
    skills: Optional[str] = Query(None, description="技能"),
    source: Optional[str] = Query(None, description="简历来源"),
    sort: Optional[str] = Query(None, description="排序方式"),
    expectedLocation: Optional[str] = Query(None, description="期望城市"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """搜索简历"""
    skip = (page - 1) * pageSize
    
    # 构建基础查询
    query = db.query(models.Resume)
    
    # 添加租户过滤
    if not current_user.is_superuser:
        query = query.filter(models.Resume.tenant_id == current_user.tenant_id)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                models.Resume.name.ilike(f"%{keyword}%"),
                models.Resume.current_company.ilike(f"%{keyword}%"),
                models.Resume.current_position.ilike(f"%{keyword}%")
            )
        )
    
    # 学历筛选
    if education:
        # 使用CASE语句将学历转换为数值进行比较
        education_level = case(
            (models.Resume.highest_education == '大专', 1),
            (models.Resume.highest_education == '本科', 2),
            (models.Resume.highest_education == '硕士', 3),
            (models.Resume.highest_education == '博士', 4),
            else_=0
        )
        
        target_level = case(
            (education == '大专', 1),
            (education == '本科', 2),
            (education == '硕士', 3),
            (education == '博士', 4),
            else_=0
        )
        
        query = query.filter(education_level >= target_level)
    
    # 工作经验筛选
    if experience:
        if experience == '0':  # 应届生
            query = query.filter(models.Resume.experience_years == 0)
        elif experience == '1-3':
            query = query.filter(models.Resume.experience_years.between(1, 3))
        elif experience == '3-5':
            query = query.filter(models.Resume.experience_years.between(3, 5))
        elif experience == '5-10':
            query = query.filter(models.Resume.experience_years.between(5, 10))
        elif experience == '10+':
            query = query.filter(models.Resume.experience_years >= 10)
    
    # 技能筛选
    if skills:
        skill_list = skills.split(',')
        # 使用json_array_elements和类型转换来处理JSON数组
        skill_conditions = []
        for skill in skill_list:
            # 使用json_array_elements和->操作符来匹配技能名称
            skill_condition = text("""
                EXISTS (
                    SELECT 1
                    FROM json_array_elements(skills::json) as skill
                    WHERE skill->>'name' = :skill_name
                )
            """)
            skill_conditions.append(skill_condition)
        
        # 将所有技能条件用AND连接
        if skill_conditions:
            query = query.filter(
                *[condition.bindparams(skill_name=skill) 
                  for condition, skill in zip(skill_conditions, skill_list)]
            )
    
    # 来源筛选
    if source:
        query = query.filter(models.Resume.source == source)
    
    # 期望城市筛选
    if expectedLocation:
        query = query.filter(
            models.Resume.expected_location.ilike(f"%{expectedLocation}%")
        )
    
    # 排序
    if sort == 'updateTime':
        query = query.order_by(models.Resume.updated_at.desc())
    elif sort == 'experience':
        query = query.order_by(models.Resume.experience_years.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    resumes = query.offset(skip).limit(pageSize).all()
    
    # 计算总页数
    total_pages = (total + pageSize - 1) // pageSize
    
    # 返回统一格式
    return {
        "data": resumes,
        "meta": {
            "total": total,
            "page": page,
            "per_page": pageSize,
            "total_pages": total_pages
        }
    }


@router.post(
    "/upload",
    response_model=ResponseMsg,
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
    file: UploadFile = File(...),
    repository_name: Optional[str] = Form(None),
    resume_type: Optional[str] = Form("general"),  # 默认为通用简历
    description: Optional[str] = Form(None),
    job_id: Optional[int] = Form(None),
    job_external_id: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """上传简历文件进行解析"""
    # 1. 快速验证
    if not resume_service.validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.filename}"
        )
    
    # 2. 快速保存文件
    file_info = await resume_service.quick_save_file(file)
    
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
    
    # 3. 快速创建简历记录
    resume = await resume_service.create_initial_resume(
        db,
        file_info,
        repository_id,
        current_user,
        job_id
    )
    
    # 4. 将简历ID加入处理队列
    process_resume_task.delay(
        resume.id,
        **{
            'job_id': job_id,
            'publisher_id': current_user.id
        }
    )
    
    return {"message": "简历上传成功，正在处理中"}


@router.get(
    "",
    response_model=ResumeListResponse,
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
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = None,
    processing_status: Optional[str] = None,
    resume_type: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取简历列表"""
    skip = (page - 1) * per_page
    
    # 构建过滤条件
    filters = {}
    if name:
        filters["name"] = name
    if processing_status:
        filters["processing_status"] = processing_status
    if resume_type:
        filters["resume_type"] = resume_type
    
    # 获取数据和总数
    resumes = resume_service.get_resumes_with_filters(
        db=db,
        tenant_id=(
            current_user.tenant_id if not current_user.is_superuser else None
        ),
        filters=filters,
        skip=skip,
        limit=per_page
    )
    
    total = resume_service.get_resumes_count_with_filters(
        db=db,
        tenant_id=(
            current_user.tenant_id if not current_user.is_superuser else None
        ),
        filters=filters
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": resumes,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.get(
    "/{resume_id}",
    response_model=Resume,
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
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取简历详情"""
    # 获取简历
    resume = resume_service.get_resume(resume_id=resume_id, db=db)
    
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
    response_model=List[Resume],
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
    response_model=ResumeParseResponse,
    summary="解析简历",
    description="根据简历ID重新解析简历文件内容",
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
    resume_id: int = Query(..., description="简历ID"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """重新解析简历内容"""
    # 获取简历
    resume = resume_service.get_resume(resume_id=resume_id, db=db)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403, 
            detail="无权解析该简历"
        )
    
    # 检查文件是否存在
    if not resume.file_path or not os.path.exists(resume.file_path):
        raise HTTPException(
            status_code=404,
            detail="简历文件不存在"
        )
    
    # 解析简历内容
    parsed_data = await resume_service._parse_and_analyze_resume(
        db,
        {
            "file_path": resume.file_path,
            "file_name": resume.file_name,
            "file_type": resume.file_type
        }
    )
    
    # 更新简历记录
    resume.content = parsed_data["content"]
    resume.parsed_data = parsed_data["parsed_data"]
    resume.processing_status = "completed"
    resume.processing_error = None
    resume.updated_at = datetime.utcnow()
    
    # 更新基本字段
    resume_fields = resume_service._extract_resume_fields(
        parsed_data["parsed_data"]
    )
    for field, value in resume_fields.items():
        if hasattr(resume, field):
            setattr(resume, field, value)
    
    db.commit()
    
    return {"parsed_data": parsed_data["parsed_data"]}


@router.put(
    "/{resume_id}",
    response_model=Resume,
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
    resume_in: ResumeUpdate,
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
    response_model=Resume,
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
    
    # 删除关联的职位申请记录
    applications = job_application_service.get_applications_by_resume(
        db=db, resume_id=resume_id
    )
    for application in applications:
        job_application_service.delete_application(
            db=db, application_id=application.id
        )
    
    # 删除关联的文件
    resume_service.delete_resume_file(resume.file_path)
    
    # 使用 remove 方法删除简历记录
    resume = resume_service.remove(db=db, id=resume_id)
    
    return resume


@router.post(
    "",
    response_model=Resume,
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
    resume_in: ResumeCreate,
    job_id: Optional[int] = Query(None, description="职位ID"),
    job_external_id: Optional[str] = Query(None, description="职位外部ID"),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """创建完整的简历信息"""
    try:
        # 准备简历数据
        resume_data = resume_in.model_dump()
        resume_data.update({
            "publisher_type": current_user.user_type or "admin",  # 设置默认发布者类型
            "publisher_id": current_user.id,
            "publisher_name": current_user.username,
            "tenant_id": current_user.tenant_id
        })
        
        resume = resume_service.create_resume_with_job(
            db=db,
            resume_data=resume_data,
            current_user=current_user,
            job_id=job_id,
            job_external_id=job_external_id,
            background_tasks=background_tasks
        )
        return resume
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{resume_id}/preview",
    response_model=Dict[str, str],
    summary="获取简历预览URL",
    description="获取简历文件的预览URL",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read"]
            )
        )
    ]
)
async def get_resume_preview_url(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """获取简历预览URL"""
    # 获取简历
    resume = resume_service.get_resume(resume_id=resume_id, db=db)
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403,
            detail="无权访问该简历"
        )
    
    # 检查文件是否存在
    if not resume.file_path or not os.path.exists(resume.file_path):
        raise HTTPException(
            status_code=404,
            detail="简历文件不存在"
        )
    
    # 获取文件类型
    file_type = resume.file_type.lower() if resume.file_type else ""
    if file_type not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型"
        )
    
    # 生成预览URL
    preview_url = f"/resumes/{resume_id}/download"
    
    return {"preview_url": preview_url}


@router.get(
    "/{resume_id}/download",
    summary="下载简历文件",
    description="下载指定的简历文件",
)
async def download_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(
        deps.get_current_active_user_from_param
    ),
    tenant_id: Optional[int] = Depends(deps.get_current_tenant_id_from_param)
) -> Any:
    """下载简历文件"""
    # 获取简历
    resume = resume_service.get_resume(resume_id=resume_id, db=db)
    
    # 检查租户权限
    if (not current_user.is_superuser and 
            resume.tenant_id != current_user.tenant_id):
        raise HTTPException(
            status_code=403,
            detail="无权访问该简历"
        )
    
    # 检查文件是否存在
    if not resume.file_path or not os.path.exists(resume.file_path):
        raise HTTPException(
            status_code=404,
            detail="简历文件不存在"
        )
    
    # 获取文件类型
    file_type = resume.file_type.lower() if resume.file_type else ""
    if file_type not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型"
        )
    
    # 设置正确的Content-Type
    media_type_map = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': (
            'application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document'
        ),
        'txt': 'text/plain',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    media_type = media_type_map.get(file_type, 'application/octet-stream')
    
    # 返回文件，设置为inline显示
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'X-Frame-Options': 'ALLOWALL'
    }
    
    return FileResponse(
        path=resume.file_path,
        filename=resume.file_name,
        media_type=media_type,
        content_disposition_type="inline",
        headers=headers
    )


@router.post(
    "/{resume_id}/ai-analysis",
    response_model=AIAnalysisResponse,
    summary="AI简历解读",
    description="使用AI对简历进行深度解读分析，评估候选人与岗位的匹配程度",
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["resume_read"]
            )
        )
    ]
)
async def analyze_resume_with_ai(
    *,
    resume_id: int = Path(..., description="简历ID"),
    analysis_request: AIAnalysisRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """使用AI对简历进行深度解读分析，评估候选人与岗位的匹配程度"""
    # 调用服务层方法进行AI分析
    result = await resume_service.analyze_resume_with_ai(
        db=db,
        resume_id=resume_id,
        analysis_request=analysis_request.dict(),
        current_user=current_user
    )
    
    return result
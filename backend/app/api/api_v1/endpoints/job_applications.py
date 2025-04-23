from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app import crud, models, schemas
from app.api import deps
from app.services.job_application_service import job_application_service
from app.services.resume_job_matching_service import (
    resume_job_matching_service
)

router = APIRouter()


@router.post(
    "",
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
    current_user_id: int = Depends(deps.get_current_user_id),
    background_tasks: BackgroundTasks
) -> Any:
    """
    创建职位申请
    - 创建新的职位申请记录
    - 验证申请数据的合法性
    - 触发后台任务处理（如通知、简历分析等）
    """
    return job_application_service.create_application_with_validation(
        db=db,
        application_in=application_in,
        tenant_id=current_tenant_id,
        created_by=current_user_id,
        background_tasks=background_tasks
    )


@router.get(
    "",
    response_model=schemas.JobApplicationListResponse,
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
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="申请状态"),
    job_title: Optional[str] = Query(None, description="职位名称"),
    candidate_name: Optional[str] = Query(None, description="候选人姓名"),
    education: Optional[str] = Query(None, description="学历要求"),
    experience: Optional[str] = Query(None, description="工作年限"),
    match_score: Optional[str] = Query(None, description="匹配度范围"),
    apply_time_start: Optional[str] = Query(None, description="申请开始时间"),
    apply_time_end: Optional[str] = Query(None, description="申请结束时间"),
    sort_field: Optional[str] = Query(None, description="排序字段"),
    sort_order: Optional[str] = Query(None, description="排序方向(asc/desc)"),
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """
    获取所有职位申请列表（跨职位，包含简历基本信息）
    - 返回当前租户下的所有职位申请
    - 包含简历的基本信息（姓名、联系方式等）
    - 支持分页查询
    - 支持多条件搜索
    - 支持排序
    """
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 构建搜索条件
    filters = {
        "tenant_id": current_tenant_id,
        "status": status,
        "job_title": job_title,
        "candidate_name": candidate_name,
        "education": education,
        "experience": experience,
        "match_score": match_score,
        "apply_time_start": apply_time_start,
        "apply_time_end": apply_time_end
    }
    
    # 获取数据和总数
    applications, total = (
        job_application_service
        .get_applications_by_tenant_with_resume_info_and_count(
            db=db,
            tenant_id=current_tenant_id,
            skip=skip,
            limit=per_page,
            filters=filters,
            sort_field=sort_field,
            sort_order=sort_order
        )
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": applications,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.get(
    "/status/{status}",
    response_model=schemas.JobApplicationListResponse,
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
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """
    获取指定状态的所有职位申请
    - 支持筛选不同状态的申请（待处理、已面试、已录用等）
    - 仅返回当前租户的申请记录
    - 支持分页查询
    - 状态值必须为系统预设的有效值
    """
    # 验证状态值是否有效
    valid_statuses = [
        "pending", "reviewed", "interviewed", 
        "offered", "rejected", "withdrawn"
    ]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"无效的状态值，有效值为: {', '.join(valid_statuses)}"
        )
    
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    applications, total = (
        job_application_service.get_applications_by_status_and_count(
            db=db, 
            status=status,
            tenant_id=current_tenant_id,
            skip=skip,
            limit=per_page
        )
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": applications,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


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
    """
    获取指定简历的所有申请
    - 查看某份简历的所有投递记录
    - 验证简历归属权（必须属于当前租户）
    - 用于跟踪求职者的申请历史
    """
    # 检查简历是否存在
    resume = crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    if resume.tenant_id != current_tenant_id:
        raise HTTPException(
            status_code=403, 
            detail="没有权限访问此简历的申请"
        )
    
    return job_application_service.get_applications_by_resume(
        db=db, resume_id=resume_id)


@router.get(
    "/{application_id}",
    response_model=schemas.JobApplicationWithResume,
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
    """
    通过ID获取职位申请信息（不需要指定职位ID，包含完整简历信息）
    - 获取单个申请的详细信息
    - 包含完整的简历内容
    - 验证租户权限
    """
    application = job_application_service.get_application_with_resume(
        db=db, 
        application_id=application_id
    )
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
    """
    更新职位申请状态
    - 修改申请的状态（如更新为已面试、已录用等）
    - 可更新申请的其他相关信息
    - 验证租户权限
    """
    application = job_application_service.get_application(
        db=db, 
        application_id=application_id
    )
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限更新此职位申请")
    
    return job_application_service.update_application(
        db=db,
        application_id=application_id,
        application_in=application_in
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
    """
    删除职位申请
    - 删除指定的职位申请记录
    - 验证租户权限
    - 软删除，保留数据但标记为已删除
    """
    application = job_application_service.get_application(
        db=db, 
        application_id=application_id
    )
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限删除此职位申请")
    
    return job_application_service.delete_application(
        db=db, 
        application_id=application_id
    )


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
    """
    获取指定职位的所有申请
    - 查看某个职位下的所有申请记录
    - 验证职位归属权（必须属于当前租户）
    - 用于职位申请的批量处理和统计
    """
    # 检查职位是否存在
    job = crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    if job.tenant_id != current_tenant_id:
        raise HTTPException(
            status_code=403, 
            detail="没有权限访问此职位的申请"
        )
    
    return job_application_service.get_applications_by_job(
        db=db, job_id=job_id)


@router.post(
    "/{application_id}/analyze-match",
    response_model=Dict[str, Any],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["job_application_update"]
            )
        )
    ]
)
async def analyze_application_match(
    *,
    db: Session = Depends(deps.get_db),
    application_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """
    手动触发简历与职位匹配度分析
    - 对指定申请进行简历与职位的匹配度分析
    - 返回匹配分数和匹配原因
    - 用于评估候选人与职位的适配程度
    - 支持异步处理大量数据
    """
    # 检查职位申请是否存在
    application = job_application_service.get_application(
        db=db, 
        application_id=application_id
    )
    if not application:
        raise HTTPException(status_code=404, detail="职位申请不存在")
    
    # 检查权限
    if application.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="没有权限分析此职位申请")
    
    # 执行匹配度分析
    result = await resume_job_matching_service.analyze_resume_job_match(
        db=db,
        application_id=application_id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"匹配度分析失败: {result.get('error', '未知错误')}"
        )
    
    return {
        "success": True,
        "match_score": result["match_score"],
        "match_reason": result["match_reason"]
    }


@router.post("/add-candidates", response_model=schemas.BatchActionResponse)
def add_candidates_from_applications(
    *,
    db: Session = Depends(deps.get_db),
    candidates_data: List[schemas.CandidateCreate],
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """将职位申请转为候选人"""
    if len(candidates_data) == 0:
        raise HTTPException(status_code=400, detail="不能提交空列表")
    
    # 检查租户权限
    tenant_id = candidates_data[0].tenant_id
    if tenant_id:
        if not deps.check_tenant_permission(db, current_user, tenant_id):
            raise HTTPException(status_code=403, detail="无权访问该租户数据")
    
    result = {"successCount": 0, "failCount": 0, "errorMessages": []}
    
    for candidate_data in candidates_data:
        try:
            # 检查是否已经存在相同的候选人记录
            existing = db.query(models.Candidate).filter(
                models.Candidate.email == candidate_data.email,
                models.Candidate.job_id == candidate_data.job_id
            ).first()
            
            if existing:
                result["failCount"] += 1
                error_msg = (
                    f"候选人 {candidate_data.name or candidate_data.email} 已存在"
                )
                result["errorMessages"].append(error_msg)
                continue
            
            # 创建新候选人
            new_candidate = models.Candidate(
                tenant_id=candidate_data.tenant_id,
                name=candidate_data.name,
                email=candidate_data.email,
                phone=candidate_data.phone,
                resume_url=candidate_data.resume_url,
                status=candidate_data.status,
                job_id=candidate_data.job_id,
                notes=candidate_data.notes,
                resume_id=candidate_data.resume_id
            )
            
            db.add(new_candidate)
            db.commit()
            result["successCount"] += 1
            
        except Exception as e:
            db.rollback()
            result["failCount"] += 1
            error_msg = (
                f"添加候选人 {candidate_data.name or candidate_data.email} "
                f"失败: {str(e)}"
            )
            result["errorMessages"].append(error_msg)
    
    return result


@router.put("/batch-status", response_model=schemas.BatchActionResponse)
def batch_update_application_status(
    *,
    db: Session = Depends(deps.get_db),
    data: schemas.ApplicationBatchUpdateRequest,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """批量更新职位申请状态"""
    if not data.ids or len(data.ids) == 0:
        raise HTTPException(status_code=400, detail="未提供申请ID列表")
    
    result = {"successCount": 0, "failCount": 0, "errorMessages": []}
    
    for app_id in data.ids:
        try:
            # 获取申请记录
            application = db.query(models.JobApplication).filter(
                models.JobApplication.id == app_id
            ).first()
            
            if not application:
                result["failCount"] += 1
                result["errorMessages"].append(f"申请ID {app_id} 不存在")
                continue
            
            # 检查租户权限
            if not deps.check_tenant_permission(
                db, current_user, application.tenant_id
            ):
                result["failCount"] += 1
                result["errorMessages"].append(f"无权更新申请 {app_id}")
                continue
            
            # 更新状态
            application.status = data.status
            if data.reviewNotes:
                application.review_notes = data.reviewNotes
            
            # 设置审核时间
            if data.status == "reviewed" and not application.review_time:
                application.review_time = datetime.utcnow()
            
            db.commit()
            result["successCount"] += 1
            
        except Exception as e:
            db.rollback()
            result["failCount"] += 1
            result["errorMessages"].append(f"更新申请 {app_id} 失败: {str(e)}")
    
    return result


@router.post("/convert-to-candidates", response_model=schemas.BatchActionResponse)
def convert_applications_to_candidates(
    *,
    db: Session = Depends(deps.get_db),
    request_data: schemas.ConvertToCandidatesRequest,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    将职位申请转为候选人并更新申请状态（一步完成）
    
    此接口将在一个事务中完成两个操作：
    1. 将申请者添加为候选人
    2. 更新申请状态为指定状态
    
    如果任一步骤失败，整个事务会回滚
    """
    if len(request_data.applications) == 0:
        raise HTTPException(status_code=400, detail="不能提交空列表")
    
    # 检查租户权限
    tenant_id = request_data.tenant_id
    if tenant_id:
        if not deps.check_tenant_permission(db, current_user, tenant_id):
            raise HTTPException(status_code=403, detail="无权访问该租户数据")
    
    result = {"successCount": 0, "failCount": 0, "errorMessages": []}
    
    for app_info in request_data.applications:
        # 开始数据库事务
        try:
            # 1. 创建候选人记录
            existing = db.query(models.Candidate).filter(
                models.Candidate.email == app_info.email,
                models.Candidate.job_id == app_info.job_id
            ).first()
            
            if existing:
                result["failCount"] += 1
                candidate_name = app_info.candidate_name or app_info.email
                error_msg = f"候选人 {candidate_name} 已存在"
                result["errorMessages"].append(error_msg)
                continue
            
            # 创建新候选人
            new_candidate = models.Candidate(
                tenant_id=app_info.tenant_id,
                name=app_info.candidate_name,
                email=app_info.email,
                phone=app_info.phone,
                resume_url=app_info.resume_url,
                status=request_data.status,
                job_id=app_info.job_id,
                notes=request_data.notes,
                resume_id=app_info.resume_id
            )
            
            db.add(new_candidate)
            
            # 2. 更新申请状态
            application = db.query(models.JobApplication).filter(
                models.JobApplication.id == app_info.id
            ).first()
            
            if not application:
                db.rollback()
                result["failCount"] += 1
                result["errorMessages"].append(f"申请ID {app_info.id} 不存在")
                continue
            
            # 更新申请状态为已审核
            application.status = "reviewed"
            application.review_notes = f"已添加为候选人: {request_data.status}"
            application.review_time = datetime.utcnow()
            
            # 提交事务
            db.commit()
            result["successCount"] += 1
            
        except Exception as e:
            db.rollback()
            result["failCount"] += 1
            error_msg = (
                f"处理申请 {app_info.id} 失败: {str(e)}"
            )
            result["errorMessages"].append(error_msg)
    
    return result 
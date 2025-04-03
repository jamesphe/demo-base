from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.job_application_service import job_application_service
from app.services.resume_job_matching_service import (
    resume_job_matching_service
)

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
    "/",
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
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """
    获取所有职位申请列表（跨职位，包含简历基本信息）
    - 返回当前租户下的所有职位申请
    - 包含简历的基本信息（姓名、联系方式等）
    - 支持分页查询
    """
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    applications, total = job_application_service.get_applications_by_tenant_with_resume_info_and_count(
        db=db,
        tenant_id=current_tenant_id,
        skip=skip,
        limit=per_page
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
    applications, total = job_application_service.get_applications_by_status_and_count(
        db=db, 
        status=status,
        tenant_id=current_tenant_id,
        skip=skip,
        limit=per_page
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
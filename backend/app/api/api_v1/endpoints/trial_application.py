from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas.trial_application import (
    TrialApplication, 
    TrialStatus,
    TrialApplicationListResponse
)
from app.services.trial_application_service import TrialApplicationService

router = APIRouter()


@router.post("/apply", response_model=TrialApplication)
def apply_for_trial(
    *,
    db: Session = Depends(deps.get_db),
    application_data: Dict[str, Any] = Body(...),
) -> Any:
    """申请试用"""
    return TrialApplicationService.apply_for_trial(db, application_data)


@router.get("/status", response_model=TrialStatus)
def get_trial_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取试用状态"""
    return TrialApplicationService.get_trial_status(db, current_user)


@router.put("/{trial_id}/approve", response_model=TrialApplication)
def approve_trial(
    *,
    db: Session = Depends(deps.get_db),
    trial_id: int,
    approval_data: Dict[str, Any] = Body(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """审批通过试用申请并创建租户及管理员账号"""
    return TrialApplicationService.approve_trial(db, trial_id, approval_data)


@router.put("/{trial_id}/reject", response_model=TrialApplication)
def reject_trial(
    *,
    db: Session = Depends(deps.get_db),
    trial_id: int,
    reason: str = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """拒绝试用申请"""
    return TrialApplicationService.reject_trial(db, trial_id, reason)


@router.get("/pending", response_model=TrialApplicationListResponse)
def get_pending_trials(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"), 
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """获取待审核的试用申请列表"""
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    trials, total = TrialApplicationService.get_pending_trials_with_count(
        db, skip=skip, limit=per_page
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": trials,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.get("/list", response_model=TrialApplicationListResponse)
def get_trial_list(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """获取所有试用申请记录"""
    # 转换分页参数
    skip = (page - 1) * per_page
    
    # 获取数据和总数
    trials, total = TrialApplicationService.get_trial_list_with_count(
        db, skip=skip, limit=per_page
    )
    
    # 计算总页数
    total_pages = (total + per_page - 1) // per_page
    
    # 返回统一格式
    return {
        "data": trials,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    } 
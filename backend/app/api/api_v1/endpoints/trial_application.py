from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services.trial_application_service import TrialApplicationService

router = APIRouter()


@router.post("/apply", response_model=schemas.TrialApplication)
def apply_for_trial(
    *,
    db: Session = Depends(deps.get_db),
    application_data: Dict[str, Any] = Body(...),
) -> Any:
    """申请试用"""
    return TrialApplicationService.apply_for_trial(db, application_data)


@router.get("/status", response_model=schemas.TrialStatus)
def get_trial_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取试用状态"""
    return TrialApplicationService.get_trial_status(db, current_user)


@router.put("/{trial_id}/approve", response_model=schemas.TrialApplication)
def approve_trial(
    *,
    db: Session = Depends(deps.get_db),
    trial_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """审批通过试用申请并创建用户账号"""
    return TrialApplicationService.approve_trial(db, trial_id)


@router.put("/{trial_id}/reject", response_model=schemas.TrialApplication)
def reject_trial(
    *,
    db: Session = Depends(deps.get_db),
    trial_id: int,
    reason: str = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """拒绝试用申请"""
    return TrialApplicationService.reject_trial(db, trial_id, reason)


@router.get("/pending", response_model=list[schemas.TrialApplication])
def get_pending_trials(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """获取待审核的试用申请列表"""
    return TrialApplicationService.get_pending_trials(db, skip=skip, limit=limit) 
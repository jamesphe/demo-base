from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.schemas.interview_feedback import (
    InterviewerFeedback, 
    InterviewerFeedbackCreate,
    InterviewerFeedbackUpdate,
    InterviewFeedbackSummary
)
from app.services.interview_feedback_service import interview_feedback_service

router = APIRouter()


@router.post(
    "/{interview_id}/feedback",
    response_model=InterviewerFeedback
)
def create_feedback(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int = Path(..., gt=0),
    feedback_in: InterviewerFeedbackCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    创建面试官反馈
    
    每个面试官可以为自己参与的面试提交反馈
    """
    # 检查面试是否存在
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查当前用户是否是面试的面试官之一
    if (current_user.id != feedback_in.interviewer_id 
            and not current_user.is_superuser):
        raise HTTPException(
            status_code=403,
            detail="只能为自己提交反馈，或者需要管理员权限"
        )
    
    # 检查面试官是否参与了这次面试
    interviewer_exists = db.query(models.interview_interviewers).filter(
        models.interview_interviewers.c.interview_id == interview_id,
        models.interview_interviewers.c.interviewer_id == feedback_in.interviewer_id
    ).first()
    
    if not interviewer_exists:
        raise HTTPException(
            status_code=403,
            detail="该面试官没有参与这次面试，不能提交反馈"
        )
    
    # 创建反馈
    feedback = interview_feedback_service.create_feedback(
        db=db,
        feedback_in=feedback_in
    )
    
    return feedback


@router.get(
    "/{interview_id}/feedback/{interviewer_id}",
    response_model=InterviewerFeedback
)
def get_interviewer_feedback(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int = Path(..., gt=0),
    interviewer_id: int = Path(..., gt=0),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取指定面试官的反馈
    
    只有本人或管理员可以查看
    """
    # 权限检查
    if current_user.id != interviewer_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="只能查看自己的反馈，或者需要管理员权限"
        )
    
    # 获取反馈
    feedback = interview_feedback_service.get_interviewer_feedback(
        db=db,
        interview_id=interview_id,
        interviewer_id=interviewer_id
    )
    
    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="未找到该面试官的反馈"
        )
    
    return feedback


@router.put(
    "/{interview_id}/feedback",
    response_model=InterviewerFeedback
)
def update_interviewer_feedback(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int = Path(..., gt=0),
    feedback_in: InterviewerFeedbackUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    更新面试官反馈
    
    系统自动使用当前用户ID作为面试官ID
    """
    # 使用当前用户ID作为面试官ID
    interviewer_id = current_user.id
    
    # 获取现有的反馈
    existing_feedback = interview_feedback_service.get_interviewer_feedback(
        db=db,
        interview_id=interview_id,
        interviewer_id=interviewer_id
    )
    
    if not existing_feedback:
        raise HTTPException(
            status_code=404,
            detail="未找到该面试官的反馈"
        )
    
    # 更新反馈
    updated_feedback = interview_feedback_service.update_feedback(
        db=db,
        interview_id=interview_id,
        interviewer_id=interviewer_id,
        feedback_in=feedback_in
    )
    
    return updated_feedback


@router.get(
    "/{interview_id}/feedback",
    response_model=List[InterviewerFeedback]
)
def get_all_feedback(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int = Path(..., gt=0),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取面试的所有反馈
    
    需要管理员权限，或是该面试的面试官
    """
    # 检查面试是否存在
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查权限
    if not current_user.is_superuser:
        # 检查当前用户是否是面试的面试官之一
        is_interviewer = db.query(models.interview_interviewers).filter(
            models.interview_interviewers.c.interview_id == interview_id,
            models.interview_interviewers.c.interviewer_id == current_user.id
        ).first()
        
        if not is_interviewer:
            raise HTTPException(
                status_code=403,
                detail="需要管理员权限或是该面试的面试官"
            )
    
    # 获取所有反馈
    feedbacks = interview_feedback_service.get_all_feedback(
        db=db,
        interview_id=interview_id
    )
    
    return feedbacks


@router.get(
    "/{interview_id}/feedback-summary",
    response_model=InterviewFeedbackSummary
)
def get_feedback_summary(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int = Path(..., gt=0),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取面试反馈汇总
    
    需要管理员权限，或是该面试的面试官
    """
    # 验证面试存在性和用户访问权限
    interview_feedback_service.verify_interview_access(
        db=db,
        interview_id=interview_id,
        current_user=current_user
    )
    
    # 获取反馈汇总
    summary = interview_feedback_service.get_feedback_summary(
        db=db,
        interview_id=interview_id
    )
    
    return summary 
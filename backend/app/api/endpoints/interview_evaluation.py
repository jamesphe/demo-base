from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services.interview_service import interview_service
from app.services.interview_evaluation_service import interview_evaluation_service
from app.services.interview_feedback_service import interview_feedback_service
from app.schemas.interview_evaluation import (
    InterviewEvaluationCreate,
    InterviewEvaluationResponse,
    InterviewEvaluationUpdate
)

router = APIRouter()


@router.post("/{interview_id}/evaluation", response_model=InterviewEvaluationResponse)
async def create_interview_evaluation(
    interview_id: int = Path(..., description="面试ID"),
    evaluation: InterviewEvaluationCreate = Body(..., description="面试评估信息"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    创建面试评估结果
    
    - 需要权限: tenant_admin 或 tenant_hr
    - 用于HR或管理员对面试进行最终评估
    """
    # 检查用户权限
    if not (current_user.is_superuser or current_user.user_type in ["tenant_admin", "tenant_hr"]):
        raise HTTPException(
            status_code=403,
            detail="无权限进行此操作"
        )
    
    # 检查面试存在性和状态
    interview = interview_service.get(db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查租户权限
    if interview.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="无权限评估此面试"
        )
    
    # 检查面试反馈是否存在
    feedback_summary = interview_feedback_service.get_interview_feedback_summary(
        db, interview_id=interview_id
    )
    if not feedback_summary or feedback_summary["completed_count"] == 0:
        raise HTTPException(
            status_code=400,
            detail="无法评估，尚未收到任何面试官反馈"
        )
    
    # 创建面试评估
    evaluation_data = evaluation.dict()
    evaluation_data.update({
        "interview_id": interview_id,
        "evaluator_id": current_user.id,
        "feedback_summary": feedback_summary
    })
    
    result = await interview_evaluation_service.create_evaluation(
        db=db,
        evaluation_in=evaluation_data
    )
    
    # 更新面试状态为已评估
    interview_service.update_interview_status(
        db=db,
        interview_id=interview_id,
        status="evaluated",
        evaluation_score=evaluation.overall_score,
        notes=f"评估完成: {evaluation.conclusion}"
    )
    
    return result


@router.get("/{interview_id}/evaluation", response_model=InterviewEvaluationResponse)
async def get_interview_evaluation(
    interview_id: int = Path(..., description="面试ID"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取面试评估详情
    
    - 需要权限: 面试相关人员或HR/管理员
    """
    # 检查面试存在性
    interview = interview_service.get(db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查租户权限
    if interview.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="无权限查看此面试评估"
        )
    
    # 获取评估结果
    evaluation = await interview_evaluation_service.get_evaluation(
        db=db,
        interview_id=interview_id
    )
    
    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="面试评估不存在"
        )
    
    return evaluation


@router.put("/{interview_id}/evaluation", response_model=InterviewEvaluationResponse)
async def update_interview_evaluation(
    interview_id: int = Path(..., description="面试ID"),
    evaluation: InterviewEvaluationUpdate = Body(..., description="面试评估更新信息"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    更新面试评估
    
    - 需要权限: tenant_admin 或 tenant_hr
    - 仅限评估完成后的修改
    """
    # 检查用户权限
    if not (current_user.is_superuser or current_user.user_type in ["tenant_admin", "tenant_hr"]):
        raise HTTPException(
            status_code=403,
            detail="无权限进行此操作"
        )
    
    # 检查面试存在性
    interview = interview_service.get(db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查租户权限
    if interview.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="无权限更新此面试评估"
        )
    
    # 获取当前评估
    current_evaluation = await interview_evaluation_service.get_evaluation(
        db=db,
        interview_id=interview_id
    )
    if not current_evaluation:
        raise HTTPException(
            status_code=404,
            detail="面试评估不存在，请先创建评估"
        )
    
    # 更新评估
    evaluation_data = evaluation.dict(exclude_unset=True)
    evaluation_data.update({
        "updated_by": current_user.id
    })
    
    result = await interview_evaluation_service.update_evaluation(
        db=db,
        interview_id=interview_id,
        evaluation_in=evaluation_data
    )
    
    # 如果更改了评分或结论，更新面试状态
    if evaluation.overall_score is not None or evaluation.conclusion is not None:
        notes = f"评估更新: {evaluation.conclusion}" if evaluation.conclusion else None
        interview_service.update_interview_status(
            db=db,
            interview_id=interview_id,
            status="evaluated",
            evaluation_score=evaluation.overall_score,
            notes=notes
        )
    
    return result


@router.get("/{interview_id}/next-step-options", response_model=List[Dict[str, Any]])
async def get_next_step_options(
    interview_id: int = Path(..., description="面试ID"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取面试后的下一步选项
    
    - 根据面试类型和结果，提供可能的下一步选项
    """
    # 检查面试存在性
    interview = interview_service.get(db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查租户权限
    if interview.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="无权限访问此面试"
        )
    
    # 获取评估结果
    evaluation = await interview_evaluation_service.get_evaluation(
        db=db,
        interview_id=interview_id
    )
    
    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="面试评估不存在，请先完成评估"
        )
    
    # 根据面试类型和评估结果生成下一步选项
    next_steps = await interview_evaluation_service.generate_next_steps(
        db=db,
        interview=interview,
        evaluation=evaluation
    )
    
    return next_steps


@router.post("/{interview_id}/proceed-to-next-step", response_model=Dict[str, Any])
async def proceed_to_next_step(
    interview_id: int = Path(..., description="面试ID"),
    next_step: Dict[str, Any] = Body(..., description="下一步操作"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    执行下一步操作
    
    - 需要权限: tenant_admin 或 tenant_hr
    - 如: 安排下一轮面试、发送offer等
    """
    # 检查用户权限
    if not (current_user.is_superuser or current_user.user_type in ["tenant_admin", "tenant_hr"]):
        raise HTTPException(
            status_code=403,
            detail="无权限进行此操作"
        )
    
    # 检查面试存在性
    interview = interview_service.get(db, id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )
    
    # 检查租户权限
    if interview.tenant_id != current_user.tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="无权限处理此面试"
        )
    
    # 执行下一步操作
    result = await interview_evaluation_service.execute_next_step(
        db=db,
        interview_id=interview_id,
        next_step=next_step,
        current_user=current_user
    )
    
    return {"message": "下一步操作已执行", "result": result} 
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("", response_model=schemas.InterviewListResponse)
def read_interviews(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取面试列表"""
    skip = (page - 1) * per_page
    if current_user.is_superuser:
        interviews = crud.interview.get_multi(db, skip=skip, limit=per_page)
        total = crud.interview.count(db)
    else:
        interviews = crud.interview.get_multi_by_tenant(
            db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=per_page
        )
        total = crud.interview.count_by_tenant(db, tenant_id=current_user.tenant_id)
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": interviews,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


@router.post(
    "",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_create"]
            )
        )
    ]
)
def create_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_in: schemas.InterviewCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新面试"""
    # 验证候选人是否存在
    candidate = crud.candidate.get(db, id=interview_in.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 验证面试官是否存在
    interviewer = crud.user.get(db, id=interview_in.interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="面试官不存在")
    
    # 检查租户权限
    if not current_user.is_superuser:
        if candidate.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="无权为该候选人安排面试")
        if interviewer.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="无权指定该面试官")
    
    interview = crud.interview.create(db=db, obj_in=interview_in)
    return interview


@router.get(
    "/candidate/{candidate_id}",
    response_model=List[schemas.InterviewWithDetails],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_read"]
            )
        )
    ]
)
def read_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取候选人的面试记录"""
    # 验证候选人是否存在
    candidate = crud.candidate.get(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该候选人的面试记录")
    
    interviews = crud.interview.get_by_candidate(db, candidate_id=candidate_id)
    return interviews


@router.get(
    "/interviewer/{interviewer_id}",
    response_model=List[schemas.InterviewWithDetails],
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_read"]
            )
        )
    ]
)
def read_interviewer_interviews(
    interviewer_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取面试官的面试安排"""
    # 验证面试官是否存在
    interviewer = crud.user.get(db, id=interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="面试官不存在")
    
    # 检查租户权限
    if not current_user.is_superuser and interviewer.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该面试官的面试安排")
    
    interviews = crud.interview.get_by_interviewer(db, interviewer_id=interviewer_id)
    return interviews


@router.put(
    "/{interview_id}",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_update"]
            )
        )
    ]
)
def update_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    interview_in: schemas.InterviewUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """更新面试信息"""
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查租户权限
    candidate = crud.candidate.get(db, id=interview.candidate_id)
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权更新该面试信息")
    
    interview = crud.interview.update(
        db=db,
        db_obj=interview,
        obj_in=interview_in
    )
    return interview


@router.delete(
    "/{interview_id}",
    response_model=schemas.Interview,
    dependencies=[
        Depends(
            deps.get_current_user_with_tenant_permission(
                required_permissions=["interview_delete"]
            )
        )
    ]
)
def delete_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """删除面试"""
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    
    # 检查租户权限
    candidate = crud.candidate.get(db, id=interview.candidate_id)
    if not current_user.is_superuser and candidate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="无权删除该面试")
    
    interview = crud.interview.remove(db=db, id=interview_id)
    return interview


@router.get("/interviewers", response_model=List[schemas.User])
def read_interviewers(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """获取面试官列表"""
    if current_user.is_superuser:
        interviewers = crud.user.get_multi_by_role(db, role="interviewer")
    else:
        interviewers = crud.user.get_multi_by_role_and_tenant(
            db,
            role="interviewer",
            tenant_id=current_user.tenant_id
        )
    return interviewers 
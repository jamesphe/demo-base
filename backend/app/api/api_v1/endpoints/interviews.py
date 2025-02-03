from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Interview])
def read_interviews(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取面试列表
    """
    interviews = crud.interview.get_multi(db, skip=skip, limit=limit)
    return interviews


@router.post("/", response_model=schemas.Interview)
def create_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_in: schemas.InterviewCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新面试
    """
    # 验证候选人是否存在
    candidate = crud.candidate.get(db, id=interview_in.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="候选人不存在"
        )
    
    # 验证面试官是否存在
    interviewer = crud.user.get(db, id=interview_in.interviewer_id)
    if not interviewer:
        raise HTTPException(
            status_code=404,
            detail="面试官不存在"
        )
    
    interview = crud.interview.create(db=db, obj_in=interview_in)
    return interview


@router.get("/candidate/{candidate_id}", response_model=List[schemas.Interview])
def read_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取候选人的面试记录
    """
    interviews = crud.interview.get_by_candidate(
        db,
        candidate_id=candidate_id,
        skip=skip,
        limit=limit
    )
    return interviews


@router.get("/interviewer/{interviewer_id}", response_model=List[schemas.Interview])
def read_interviewer_interviews(
    interviewer_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取面试官的面试安排
    """
    interviews = crud.interview.get_by_interviewer(
        db,
        interviewer_id=interviewer_id,
        skip=skip,
        limit=limit
    )
    return interviews


@router.put("/{interview_id}", response_model=schemas.Interview)
def update_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    interview_in: schemas.InterviewUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新面试信息
    """
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    interview = crud.interview.update(
        db=db,
        db_obj=interview,
        obj_in=interview_in
    )
    return interview


@router.delete("/{interview_id}", response_model=schemas.Interview)
def delete_interview(
    *,
    db: Session = Depends(deps.get_db),
    interview_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    删除面试
    """
    interview = crud.interview.get(db=db, id=interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")
    interview = crud.interview.remove(db=db, id=interview_id)
    return interview 
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Candidate])
def read_candidates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取候选人列表
    """
    candidates = crud.candidate.get_multi(db, skip=skip, limit=limit)
    return candidates


@router.post("/", response_model=schemas.Candidate)
def create_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_in: schemas.CandidateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    创建新候选人
    """
    candidate = crud.candidate.get_by_email(db, email=candidate_in.email)
    if candidate:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )
    candidate = crud.candidate.create(db=db, obj_in=candidate_in)
    return candidate


@router.get("/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(
    *,
    db: Session = Depends(deps.get_db),
    candidate_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取指定候选人信息
    """
    candidate = crud.candidate.get(db=db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    return candidate 
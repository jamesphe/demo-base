from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.services.skill_service import SkillService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=SkillResponse)
def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建技能"""
    service = SkillService(db)
    return service.create_skill(skill)


@router.get("/", response_model=List[SkillResponse])
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取技能列表"""
    service = SkillService(db)
    return service.list_skills(skip=skip, limit=limit)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新技能信息"""
    service = SkillService(db)
    updated_skill = service.update_skill(skill_id, skill)
    if not updated_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated_skill 
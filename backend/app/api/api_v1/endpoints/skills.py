from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
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
    # 如果是租户用户,则创建租户专属技能
    tenant_id = current_user.tenant_id if current_user.user_type == 'tenant' else None
    return service.create_skill(skill, tenant_id=tenant_id)


@router.get("/", response_model=List[SkillResponse])
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取技能列表"""
    service = SkillService(db)
    # 如果是租户用户,则只返回该租户的技能和公共技能
    tenant_id = current_user.tenant_id if current_user.user_type == 'tenant' else None
    return service.list_skills(skip=skip, limit=limit, tenant_id=tenant_id)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新技能信息"""
    service = SkillService(db)
    # 如果是租户用户,则只能更新该租户的技能
    tenant_id = current_user.tenant_id if current_user.user_type == 'tenant' else None
    updated_skill = service.update_skill(skill_id, skill, tenant_id=tenant_id)
    if not updated_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated_skill 
from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services.skill_service import skill_service  # 直接导入实例

router = APIRouter()

@router.post("/", response_model=schemas.Skill)
def create_skill(
    *,
    db: Session = Depends(deps.get_db),
    skill_in: schemas.SkillCreate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """创建技能"""
    # 不需要创建新的服务实例，直接使用导入的实例
    return skill_service.create_skill(db=db, skill=skill_in, tenant_id=current_tenant_id)

@router.get("/", response_model=List[schemas.Skill])
def list_skills(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """获取技能列表"""
    return skill_service.list_skills(
        db=db,
        skip=skip,
        limit=limit,
        tenant_id=current_tenant_id
    )

@router.get("/{skill_id}", response_model=schemas.Skill)
def get_skill(
    *,
    db: Session = Depends(deps.get_db),
    skill_id: int,
) -> Any:
    """获取单个技能"""
    return skill_service.get_skill(db=db, skill_id=skill_id)

@router.put("/{skill_id}", response_model=schemas.Skill)
def update_skill(
    *,
    db: Session = Depends(deps.get_db),
    skill_id: int,
    skill_in: schemas.SkillUpdate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
) -> Any:
    """更新技能"""
    return skill_service.update_skill(
        db=db,
        skill_id=skill_id,
        skill_update=skill_in,
        tenant_id=current_tenant_id
    ) 
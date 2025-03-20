from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.talent_experience import (
    TalentExperienceCreate,
    TalentExperienceUpdate,
    TalentExperienceResponse
)
from app.services.talent_experience_service import ExperienceService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=TalentExperienceResponse)
def create_experience(
    experience: TalentExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建工作经验"""
    service = ExperienceService(db)
    return service.create_experience(experience)


@router.get("/talent/{talent_id}", response_model=List[TalentExperienceResponse])
def list_talent_experiences(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才的所有工作经验"""
    service = ExperienceService(db)
    return service.list_talent_experiences(talent_id)


@router.put("/{experience_id}", response_model=TalentExperienceResponse)
def update_experience(
    experience_id: int,
    experience: TalentExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新工作经验"""
    service = ExperienceService(db)
    updated = service.update_experience(experience_id, experience)
    if not updated:
        raise HTTPException(status_code=404, detail="Experience not found")
    return updated


@router.delete("/{experience_id}")
def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除工作经验"""
    service = ExperienceService(db)
    if not service.delete_experience(experience_id):
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"message": "Experience deleted successfully"} 
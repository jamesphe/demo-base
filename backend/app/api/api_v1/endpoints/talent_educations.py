from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.talent_education import (
    TalentEducationCreate,
    TalentEducationUpdate,
    TalentEducationResponse
)
from app.services.talent_education_service import EducationService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("", response_model=TalentEducationResponse)
def create_education(
    education: TalentEducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建教育经历"""
    service = EducationService(db)
    return service.create_education(education)


@router.get("/talent/{talent_id}", response_model=List[TalentEducationResponse])
def list_talent_educations(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才的所有教育经历"""
    service = EducationService(db)
    return service.list_talent_educations(talent_id)


@router.put("/{education_id}", response_model=TalentEducationResponse)
def update_education(
    education_id: int,
    education: TalentEducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新教育经历"""
    service = EducationService(db)
    updated = service.update_education(education_id, education)
    if not updated:
        raise HTTPException(status_code=404, detail="Education not found")
    return updated


@router.delete("/{education_id}")
def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除教育经历"""
    service = EducationService(db)
    if not service.delete_education(education_id):
        raise HTTPException(status_code=404, detail="Education not found")
    return {"message": "Education deleted successfully"} 
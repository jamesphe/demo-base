from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.talent_certification import (
    TalentCertificationCreate,
    TalentCertificationUpdate,
    TalentCertificationResponse
)
from app.services.talent_certification_service import CertificationService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=TalentCertificationResponse)
def create_certification(
    certification: TalentCertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建认证信息"""
    service = CertificationService(db)
    return service.create_certification(certification)


@router.get("/{certification_id}", response_model=TalentCertificationResponse)
def get_certification(
    certification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个认证详情"""
    service = CertificationService(db)
    certification = service.get_certification(certification_id)
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification


@router.get("/talent/{talent_id}", response_model=List[TalentCertificationResponse])
def list_talent_certifications(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才的所有认证"""
    service = CertificationService(db)
    return service.list_talent_certifications(talent_id)


@router.put("/{certification_id}", response_model=TalentCertificationResponse)
def update_certification(
    certification_id: int,
    certification: TalentCertificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新认证信息"""
    service = CertificationService(db)
    updated = service.update_certification(certification_id, certification)
    if not updated:
        raise HTTPException(status_code=404, detail="Certification not found")
    return updated


@router.delete("/{certification_id}")
def delete_certification(
    certification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除认证信息"""
    service = CertificationService(db)
    if not service.delete_certification(certification_id):
        raise HTTPException(status_code=404, detail="Certification not found")
    return {"message": "Certification deleted successfully"} 
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from app.schemas.talent import TalentCreate, TalentUpdate, TalentResponse
from app.services.talent_service import TalentService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=TalentResponse)
def create_talent(
    talent: TalentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建人才信息"""
    service = TalentService(db)
    return service.create_talent(talent)


@router.get("/{talent_id}", response_model=TalentResponse)
def get_talent(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个人才详情"""
    service = TalentService(db)
    talent = service.get_talent(talent_id)
    if not talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    return talent


@router.put("/{talent_id}", response_model=TalentResponse)
def update_talent(
    talent_id: int,
    talent: TalentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新人才信息"""
    service = TalentService(db)
    updated_talent = service.update_talent(talent_id, talent)
    if not updated_talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    return updated_talent


@router.get("/", response_model=List[TalentResponse])
def list_talents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才列表"""
    service = TalentService(db)
    return service.list_talents(skip=skip, limit=limit)


@router.delete("/{talent_id}")
def delete_talent(
    talent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除人才信息"""
    service = TalentService(db)
    if not service.delete_talent(talent_id):
        raise HTTPException(status_code=404, detail="Talent not found")
    return {"message": "Talent deleted successfully"} 
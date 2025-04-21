from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.talent_pool import (
    TalentPoolCreate,
    TalentPoolUpdate,
    TalentPoolResponse,
    TalentPoolMemberCreate,
    TalentPoolMemberResponse
)
from app.services.talent_pool_service import TalentPoolService
from app.api.deps import get_current_user, get_db
from app.models.user import User


router = APIRouter()


@router.post("", response_model=TalentPoolResponse)
def create_pool(
    pool: TalentPoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建人才库"""
    service = TalentPoolService(db)
    return service.create_pool(pool)


@router.get("/{pool_id}", response_model=TalentPoolResponse)
def get_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才库详情"""
    service = TalentPoolService(db)
    pool = service.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Talent pool not found")
    return pool


@router.get("/tenant/{tenant_id}", response_model=List[TalentPoolResponse])
def list_tenant_pools(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取租户的所有人才库"""
    service = TalentPoolService(db)
    return service.list_tenant_pools(tenant_id)


@router.put("/{pool_id}", response_model=TalentPoolResponse)
def update_pool(
    pool_id: int,
    pool: TalentPoolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新人才库信息"""
    service = TalentPoolService(db)
    updated_pool = service.update_pool(pool_id, pool)
    if not updated_pool:
        raise HTTPException(status_code=404, detail="Talent pool not found")
    return updated_pool


@router.delete("/{pool_id}")
def delete_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除人才库"""
    service = TalentPoolService(db)
    if not service.delete_pool(pool_id):
        raise HTTPException(status_code=404, detail="Talent pool not found")
    return {"message": "Talent pool deleted successfully"}


@router.post("/members", response_model=TalentPoolMemberResponse)
def add_pool_member(
    member: TalentPoolMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加人才库成员"""
    service = TalentPoolService(db)
    return service.add_member(member)


@router.delete("/members/{member_id}")
def remove_pool_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """移除人才库成员"""
    service = TalentPoolService(db)
    if not service.remove_member(member_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member removed successfully"}


@router.get(
    "/{pool_id}/members",
    response_model=List[TalentPoolMemberResponse]
)
def list_pool_members(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取人才库所有成员"""
    service = TalentPoolService(db)
    return service.list_pool_members(pool_id) 
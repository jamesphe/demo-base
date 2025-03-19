from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    获取用户列表
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """创建新用户"""
    return user_service.create_user(
        db, 
        user_in=user_in, 
        current_user=current_user
    )


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    username: str = Body(None),
    email: str = Body(None),
    user_type: str = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新当前用户信息
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if username is not None:
        user_in.username = username
    if email is not None:
        user_in.email = email
    if user_type is not None:
        if current_user.is_superuser:
            user_in.user_type = user_type
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/info", response_model=schemas.UserInfoResponse)
def get_user_info(
    current_user: models.User = Depends(deps.get_current_user)
):
    """获取当前登录用户信息"""
    user_info = schemas.UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=current_user.username,
        user_type=current_user.user_type,
        avatar=current_user.avatar,
        introduction=current_user.introduction,
        roles=current_user.get_roles(),
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        tenant_id=current_user.tenant_id
    )
    
    return {
        "code": 20000,
        "data": user_info
    }


@router.get("/types/{type}", response_model=List[schemas.User])
def get_users_by_type(
    type: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    按用户类型获取用户列表
    """
    users = crud.user.get_by_type(db, user_type=type, skip=skip, limit=limit)
    return users


@router.post("/batch", response_model=List[schemas.User])
def create_users_batch(
    *,
    db: Session = Depends(deps.get_db),
    users_in: List[schemas.UserCreate],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """批量创建用户"""
    return user_service.bulk_create_users(
        db,
        users_in=users_in,
        current_user=current_user
    )


@router.put("/batch", response_model=List[schemas.User])
def update_users_batch(
    *,
    db: Session = Depends(deps.get_db),
    updates: List[schemas.UserUpdate],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """批量更新用户"""
    users = []
    for update in updates:
        user = crud.user.get(db, id=update.id)
        if user:
            users.append(crud.user.update(db, db_obj=user, obj_in=update))
    return users


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """更新用户信息(包括状态)"""
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return crud.user.update(db, db_obj=user, obj_in=user_update)


@router.get("/search", response_model=List[schemas.User])
def search_users(
    *,
    db: Session = Depends(deps.get_db),
    keyword: str,
    user_type: Optional[str] = None,
    tenant_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """搜索用户"""
    return user_service.search_users(
        db,
        keyword=keyword,
        user_type=user_type,
        tenant_id=tenant_id,
        is_active=is_active,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """删除用户"""
    return user_service.delete_user(
        db=db,
        user_id=user_id,
        current_user=current_user
    ) 
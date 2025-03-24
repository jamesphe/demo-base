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


@router.put("/{user_id}/roles", response_model=schemas.User)
def update_user_roles(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_ids: List[int] = Body(..., description="角色ID列表"),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    更新用户角色
    """
    # 获取用户
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 验证所有角色ID是否存在
    for role_id in role_ids:
        role = crud.role.get(db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"角色ID {role_id} 不存在"
            )
    
    # 直接操作关联表
    # 1. 删除所有现有关联
    db.execute("DELETE FROM user_role WHERE user_id = :user_id", {"user_id": user_id})
    
    # 2. 添加新的关联
    for role_id in role_ids:
        db.execute(
            "INSERT INTO user_role (user_id, role_id) VALUES (:user_id, :role_id)",
            {"user_id": user_id, "role_id": role_id}
        )
    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/{user_id}/roles")
def get_user_roles(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取用户的角色列表
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 检查权限：只有超级管理员或者用户本人可以查看角色
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="无权查看其他用户的角色"
        )
    
    # 返回角色的基本信息，而不是完整的Role对象
    return [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]


@router.post("/batch-roles", response_model=List[schemas.User])
def update_users_roles_batch(
    *,
    db: Session = Depends(deps.get_db),
    user_roles: List[schemas.UserRoleUpdate] = Body(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """批量更新用户角色"""
    updated_users = []
    
    for user_role in user_roles:
        user = crud.user.get(db, id=user_role.user_id)
        if not user:
            continue
            
        # 获取所有指定的角色
        roles = []
        for role_id in user_role.role_ids:
            role = crud.role.get(db, id=role_id)
            if role:
                roles.append(role)
        
        # 更新用户的角色
        user.roles = roles
        db.add(user)
        updated_users.append(user)
    
    db.commit()
    
    # 刷新所有更新的用户对象
    for user in updated_users:
        db.refresh(user)
    
    return updated_users


@router.post("/{user_id}/roles/{role_id}", response_model=schemas.User)
def add_user_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    为用户添加特定角色
    """
    # 获取用户
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 获取角色
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    
    # 检查角色是否已经分配给用户
    if role in user.roles:
        return user  # 角色已存在，直接返回用户
    
    # 添加角色关联
    db.execute(
        "INSERT INTO user_role (user_id, role_id) VALUES (:user_id, :role_id)",
        {"user_id": user_id, "role_id": role_id}
    )
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=schemas.User)
def remove_user_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    从用户中移除特定角色
    """
    # 获取用户
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 获取角色
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    
    # 检查角色是否已分配给用户
    if role not in user.roles:
        return user  # 角色不存在，直接返回用户
    
    # 删除角色关联
    db.execute(
        "DELETE FROM user_role WHERE user_id = :user_id AND role_id = :role_id",
        {"user_id": user_id, "role_id": role_id}
    )
    
    db.commit()
    db.refresh(user)
    
    return user
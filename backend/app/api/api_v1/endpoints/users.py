from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=schemas.UserListResponse)
def read_users(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取用户列表
    超级管理员可以获取所有用户
    租户管理员只能获取其租户下的用户
    """
    skip = (page - 1) * per_page
    users = user_service.get_users(
        db, 
        current_user=current_user, 
        skip=skip, 
        limit=per_page
    )
    total = user_service.count_users(db, current_user=current_user)
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": users,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


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


@router.get("/search", response_model=schemas.UserListResponse)
def search_users(
    *,
    db: Session = Depends(deps.get_db),
    keyword: str,
    user_type: Optional[str] = None,
    tenant_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
) -> Any:
    """搜索用户"""
    # 检查是否为超级管理员
    if not current_user.is_superuser and current_user.user_type != 'tenant':
        raise HTTPException(
            status_code=400,
            detail="该操作需要超级管理员或租户管理员权限"
        )
    
    skip = (page - 1) * per_page
    
    # 非管理员只能搜索本租户用户
    if not current_user.is_superuser:
        tenant_id = current_user.tenant_id
        
    users = user_service.search_users(
        db,
        keyword=keyword,
        user_type=user_type,
        tenant_id=tenant_id,
        is_active=is_active,
        skip=skip,
        limit=per_page
    )
    
    # 增加租户和角色信息
    enhanced_users = []
    for user in users:
        # 获取用户角色信息
        roles = [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
            for role in user.roles
        ]
        
        # 获取角色名称列表
        role_names = [role["description"] for role in roles]
        
        # 获取租户信息
        tenant = None
        tenant_name = None
        if user.tenant_id:
            tenant = crud.tenant.get(db, id=user.tenant_id)
            if tenant:
                tenant_name = tenant.tenant_name
                tenant = {
                    "id": tenant.id,
                    "name": tenant.tenant_name,
                    "code": str(tenant.id)
                }
        
        # 创建增强的用户信息
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type,
            "avatar": user.avatar,
            "introduction": user.introduction,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "tenant_id": user.tenant_id,
            "tenant_name": tenant_name,
            "role_names": role_names,
            "phone": getattr(user, 'phone', None),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": roles,
            "tenant": tenant
        }
        enhanced_users.append(user_dict)
    
    total = user_service.count_search_users(
        db,
        keyword=keyword,
        user_type=user_type,
        tenant_id=tenant_id,
        is_active=is_active
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": enhanced_users,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }


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
    print("更新用户角色 - 接收到的参数:", {
        "user_id": user_id,
        "role_ids": role_ids,
        "role_ids_type": type(role_ids),
        "role_ids_items": [{"value": id, "type": type(id)} for id in role_ids] if isinstance(role_ids, list) else None,
        "request_body": Body.get_default(),
    })
    
    try:
        result = user_service.update_user_roles(
            db,
            user_id=user_id,
            role_ids=role_ids,
            current_user=current_user
        )
        print("更新用户角色 - 成功:", {
            "user_id": result.id,
            "roles": [{"id": r.id, "name": r.name} for r in result.roles]
        })
        return result
    except Exception as e:
        print("更新用户角色 - 错误:", {
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "user_id": user_id,
            "role_ids": role_ids
        })
        raise


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
    return [
        {"id": role.id, "name": role.name, "description": role.description} 
        for role in user.roles
    ]


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
    return user_service.add_user_role(
        db,
        user_id=user_id,
        role_id=role_id,
        current_user=current_user
    )


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
    return user_service.remove_user_role(
        db,
        user_id=user_id,
        role_id=role_id,
        current_user=current_user
    )
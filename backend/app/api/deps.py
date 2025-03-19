from typing import Generator, List, Any, Callable
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭据",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="该操作需要超级管理员权限"
        )
    return current_user

def check_permissions(
    security_scopes: SecurityScopes,
    current_user: User = Depends(get_current_active_user),
) -> bool:
    """检查当前用户是否拥有所需权限"""
    if not security_scopes.scopes:
        return True
        
    for scope in security_scopes.scopes:
        if not current_user.has_permission(scope):
            raise HTTPException(
                status_code=403,
                detail=f"权限不足。需要权限: {scope}"
            )
    return True

def get_current_user_with_tenant_permission(
    required_permissions: List[str] = [],
    check_tenant: bool = True
) -> Callable:
    """创建一个依赖,用于检查用户权限和租户权限"""
    def dependency(
        security_scopes: SecurityScopes,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        tenant_id: int = None,
    ) -> User:
        # 检查基本权限
        for permission in required_permissions:
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足。需要权限: {permission}"
                )
        
        # 检查租户权限
        if check_tenant and tenant_id:
            if not check_tenant_permission(db, current_user, tenant_id):
                raise HTTPException(
                    status_code=403,
                    detail="无权访问该租户数据"
                )
        
        return current_user

    return dependency

def check_tenant_permission(
    db: Session,
    current_user: User,
    resource_tenant_id: int
) -> bool:
    """检查用户是否有权限访问指定租户的数据"""
    # 超级管理员可以访问所有租户数据
    if current_user.is_superuser:
        return True
        
    # 检查用户是否属于该租户
    return current_user.tenant_id == resource_tenant_id

def get_current_tenant_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    验证当前用户是否为租户用户
    """
    if current_user.user_type != 'tenant':
        raise HTTPException(
            status_code=403,
            detail="该操作仅允许租户用户执行"
        )
    return current_user

def get_current_candidate(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    验证当前用户是否为求职者
    """
    if current_user.user_type != 'candidate':
        raise HTTPException(
            status_code=403,
            detail="该操作仅允许求职者执行"
        )
    return current_user 
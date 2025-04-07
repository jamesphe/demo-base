from typing import Generator, List, Any, Callable, Optional
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

# 标准的OAuth2认证，用于大多数API
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# 可选的OAuth2认证，用于支持URL参数认证的API
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False
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
) -> models.User:
    """获取当前用户"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
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

async def get_token_from_request(
    request: Request,
    authorization: Optional[str] = Depends(optional_oauth2_scheme)
) -> Optional[str]:
    """从请求中获取token，支持header和URL参数"""
    # 从header中获取token
    if authorization:
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() == 'bearer':
            return token
    
    # 从URL参数获取token
    token = request.query_params.get('token')
    if token:
        return token
    
    return None

async def get_current_user_from_token_or_param(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> models.User:
    """从header或URL参数中获取token并验证用户"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """获取当前活跃用户"""
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_user_from_param(
    current_user: models.User = Depends(get_current_user_from_token_or_param),
) -> models.User:
    """获取当前活跃用户（支持URL参数认证）"""
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="该操作需要超级管理员权限"
        )
    return current_user

def check_permissions(
    security_scopes: SecurityScopes,
    current_user: models.User = Depends(get_current_active_user),
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
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        tenant_id: int = None,
    ) -> models.User:
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
    current_user: models.User,
    resource_tenant_id: int
) -> bool:
    """检查用户是否有权限访问指定租户的数据"""
    # 超级管理员可以访问所有租户数据
    if current_user.is_superuser:
        return True
        
    # 检查用户是否属于该租户
    return current_user.tenant_id == resource_tenant_id

def get_current_tenant_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
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
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    验证当前用户是否为求职者
    """
    if current_user.user_type != 'candidate':
        raise HTTPException(
            status_code=403,
            detail="该操作仅允许求职者执行"
        )
    return current_user

def get_current_tenant_id(
    current_user: models.User = Depends(get_current_user)
) -> Optional[int]:
    """获取当前租户ID"""
    if current_user.user_type == 'tenant':
        return current_user.tenant_id
    return None

def get_current_user_id(
    current_user: models.User = Depends(get_current_user)
) -> int:
    """获取当前用户ID"""
    return current_user.id

def get_current_tenant_id_from_param(
    current_user: models.User = Depends(get_current_user_from_token_or_param)
) -> Optional[int]:
    """获取当前租户ID（支持URL参数认证）"""
    if current_user.user_type == 'tenant':
        return current_user.tenant_id
    return None

def get_current_user_id_from_param(
    current_user: models.User = Depends(get_current_user_from_token_or_param)
) -> int:
    """获取当前用户ID（支持URL参数认证）"""
    return current_user.id 
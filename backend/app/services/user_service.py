from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from jose import jwt

from app import models, schemas
from app.schemas.user import UserCreate, UserUpdate, UserType
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from .base import BaseService
from app import crud
from app.services import tenant_service


class UserService(BaseService[models.User, UserCreate, UserUpdate]):
    """用户服务"""
    
    def __init__(self):
        super().__init__(models.User)

    def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[models.User]:
        """用户认证"""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_by_email(
        self,
        db: Session,
        *,
        email: str
    ) -> Optional[models.User]:
        """根据邮箱获取用户"""
        return db.query(models.User).filter(
            models.User.email == email
        ).first()

    def create_user(
        self,
        db: Session,
        *,
        user_in: schemas.UserCreate,
        current_user: models.User
    ) -> models.User:
        """创建用户"""
        try:
            # 检查创建权限
            self._check_create_permission(current_user, user_in)
            
            # 检查邮箱是否已注册
            if crud.user.get_by_email(db, email=user_in.email):
                raise HTTPException(
                    status_code=400,
                    detail="该邮箱已被注册"
                )
            
            # 处理租户关联
            user_in.tenant_id = tenant_service.process_tenant_id(db, user_in)
            
            return crud.user.create(db, obj_in=user_in)
        except ValueError as e:
            if "user_type" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail=f"用户类型必须是以下之一: {', '.join([t.value for t in schemas.UserType])}"
                )
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    def _check_create_permission(
        self,
        current_user: models.User,
        user_in: schemas.UserCreate
    ) -> None:
        """检查创建用户权限"""
        if not current_user.is_superuser:
            if (current_user.user_type != 'tenant' or 
                user_in.user_type not in ['tenant', 'candidate']):
                raise HTTPException(
                    status_code=403,
                    detail="没有权限创建该类型用户"
                )
            user_in.tenant_id = current_user.tenant_id

    def create_access_token(
        self,
        *,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        to_encode = {
            "exp": expire,
            "sub": str(user_id)
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def update_password(
        self,
        db: Session,
        *,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> models.User:
        """更新密码"""
        user = self.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="当前密码错误")
            
        hashed_password = get_password_hash(new_password)
        return self.update(
            db,
            db_obj=user,
            obj_in={"hashed_password": hashed_password}
        )

    def get_user_info(
        self,
        db: Session,
        *,
        user_id: int
    ) -> Dict[str, Any]:
        """获取用户信息"""
        user = self.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "avatar": user.avatar,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at
        }

    def bulk_create_users(
        self,
        db: Session,
        *,
        users_in: List[schemas.UserCreate],
        current_user: models.User
    ) -> List[models.User]:
        """批量创建用户"""
        users = []
        for user_in in users_in:
            users.append(self.create_user(
                db,
                user_in=user_in,
                current_user=current_user
            ))
        return users

    def search_users(
        self,
        db: Session,
        keyword: str,
        user_type: Optional[UserType] = None,
        tenant_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        current_user: models.User = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.User]:
        """搜索用户"""
        # 非管理员只能搜索本租户用户
        if not current_user.is_superuser:
            tenant_id = current_user.tenant_id
            
        return crud.user.search(
            db,
            keyword=keyword,
            user_type=user_type,
            tenant_id=tenant_id,
            is_active=is_active,
            skip=skip,
            limit=limit
        )

    def update_user_status(
        self,
        db: Session,
        *,
        user_id: int,
        is_active: bool,
        current_user: models.User
    ) -> models.User:
        """更新用户状态"""
        user = crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )
        
        user_in = schemas.UserUpdate(is_active=is_active)
        return crud.user.update(db, db_obj=user, obj_in=user_in)

    def delete_user(self, db: Session, user_id: int, current_user: models.User) -> models.User:
        """删除用户
        
        Args:
            db: 数据库会话
            user_id: 要删除的用户ID
            current_user: 当前操作的用户
            
        Raises:
            HTTPException: 用户不存在或者试图删除超级管理员时抛出
        """
        user = crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        # 不允许删除超级管理员
        if user.is_superuser:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete superuser"
            )
        return crud.user.remove(db=db, id=user_id)


# 创建服务实例
user_service = UserService()

# 只导出实例
__all__ = ["user_service"] 
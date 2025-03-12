from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from jose import jwt

from app import models, schemas
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from .base import BaseService


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
        obj_in: UserCreate
    ) -> models.User:
        """创建用户"""
        # 检查邮箱是否已存在
        db_obj = self.get_by_email(db, email=obj_in.email)
        if db_obj:
            raise HTTPException(
                status_code=400,
                detail="邮箱已被注册"
            )
            
        # 创建用户
        db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            tenant_id=obj_in.tenant_id,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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


# 创建服务实例
user_service = UserService()

# 只导出实例
__all__ = ["user_service"] 
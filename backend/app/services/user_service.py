from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy.sql import expression
from sqlalchemy import or_
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
            
            # 检查手机号是否已注册
            if user_in.phone and crud.user.get_by_phone(db, phone=user_in.phone):
                raise HTTPException(
                    status_code=400, 
                    detail="该手机号已被注册"
                )
            
            # 处理租户关联
            user_in.tenant_id = tenant_service.process_tenant_id(db, user_in)
            
            return crud.user.create(db, obj_in=user_in)
        except ValueError as e:
            if "user_type" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"用户类型必须是以下之一: "
                        f"{', '.join([t.value for t in schemas.UserType])}"
                    )
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
            if (
                current_user.user_type != 'tenant' or 
                user_in.user_type not in ['tenant', 'candidate']
            ):
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
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.User]:
        """搜索用户"""
        # 直接使用 crud 层的 search 方法
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

    def delete_user(
        self, 
        db: Session, 
        user_id: int, 
        current_user: models.User
    ) -> models.User:
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

    def get_users(
        self,
        db: Session,
        current_user: models.User,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.User]:
        """获取用户列表"""
        # 检查是否为超级管理员
        if not current_user.is_superuser and current_user.user_type != 'tenant':
            raise HTTPException(
                status_code=400,
                detail="该操作需要超级管理员或租户管理员权限"
            )
        
        if current_user.is_superuser:
            users = crud.user.get_multi(
                db, 
                skip=skip, 
                limit=limit
            )
        else:
            users = crud.user.search(
                db,
                keyword="",  # 如果不需要关键词搜索,传空字符串
                tenant_id=current_user.tenant_id,
                skip=skip,
                limit=limit
            )
        return users

    def count_users(
        self,
        db: Session,
        current_user: models.User
    ) -> int:
        """获取用户总数"""
        if current_user.is_superuser:
            return crud.user.count(db)
        return crud.user.count_by_tenant(db, tenant_id=current_user.tenant_id)

    def update_user_roles(
        self,
        db: Session,
        user_id: int,
        role_ids: List[int],
        current_user: models.User
    ) -> models.User:
        """更新用户角色"""
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
        db.execute(
            "DELETE FROM user_role WHERE user_id = :user_id", 
            {"user_id": user_id}
        )
        
        # 2. 添加新的关联
        for role_id in role_ids:
            db.execute(
                "INSERT INTO user_role (user_id, role_id) VALUES (:user_id, :role_id)",
                {"user_id": user_id, "role_id": role_id}
            )
        
        db.commit()
        db.refresh(user)
        
        return user

    def add_user_role(
        self,
        db: Session,
        user_id: int,
        role_id: int,
        current_user: models.User
    ) -> models.User:
        """为用户添加特定角色"""
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
            """
            INSERT INTO user_role (user_id, role_id) 
            VALUES (:user_id, :role_id)
            """,
            {"user_id": user_id, "role_id": role_id}
        )
        
        db.commit()
        db.refresh(user)
        
        return user

    def remove_user_role(
        self,
        db: Session,
        user_id: int,
        role_id: int,
        current_user: models.User
    ) -> models.User:
        """从用户中移除特定角色"""
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
            """
            DELETE FROM user_role 
            WHERE user_id = :user_id AND role_id = :role_id
            """,
            {"user_id": user_id, "role_id": role_id}
        )
        
        db.commit()
        db.refresh(user)
        
        return user

    def count_search_users(
        self,
        db: Session,
        keyword: str,
        user_type: Optional[UserType] = None,
        tenant_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """统计搜索结果总数"""
        query = db.query(models.User)
        
        # 构建过滤条件
        if keyword:
            query = query.filter(
                or_(
                    models.User.username.ilike(f"%{keyword}%"),
                    models.User.email.ilike(f"%{keyword}%")
                )
            )
        if user_type:
            query = query.filter(models.User.user_type == user_type)
        if tenant_id is not None:
            query = query.filter(models.User.tenant_id == tenant_id)
        if is_active is not None:
            query = query.filter(models.User.is_active == is_active)
        
        return query.count()


# 创建服务实例
user_service = UserService()

# 只导出实例
__all__ = ["user_service"] 
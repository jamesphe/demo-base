from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.core.logging_config import setup_logger

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# 使用统一的日志配置
logger = setup_logger(__name__)

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        logger.debug(f"Looking up user by email: {email}")
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            avatar=obj_in.avatar,
            introduction=obj_in.introduction,
            user_type=obj_in.user_type,
            is_superuser=obj_in.is_superuser,
            tenant_id=obj_in.tenant_id,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        logger.debug(f"Attempting to authenticate user: {email}")
        user = self.get_by_email(db, email=email)
        if user:
            logger.debug(
                f"User found: {user.email}, "
                f"{user.hashed_password[:10]}..."
            )
        else:
            logger.debug("No user found")
        
        if not user:
            logger.warning(f"User not found: {email}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.debug(
                f"password: {password}, "
                f"user.hashed_password: {user.hashed_password}"
            )
            logger.warning(f"Invalid password for user: {email}")
            return None
        logger.debug(f"User authenticated successfully: {email}")
        return user

    def is_active(self, user: User) -> bool:
        logger.debug(f"Checking if user is active: {user.email}")
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        logger.debug(f"Checking if user is superuser: {user.email}")
        return user.is_superuser

    def search(
        self,
        db: Session,
        *,
        keyword: str,
        user_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """搜索用户
        
        Args:
            db: 数据库会话
            keyword: 搜索关键词(用户名或邮箱)
            user_type: 用户类型过滤
            tenant_id: 租户ID过滤
            is_active: 是否激活过滤
            skip: 分页起始位置
            limit: 分页大小
        """
        query = db.query(self.model)
        
        # 构建搜索条件
        filters = []
        if keyword:
            filters.append(
                or_(
                    self.model.username.ilike(f"%{keyword}%"),
                    self.model.email.ilike(f"%{keyword}%")
                )
            )
        if user_type:
            filters.append(self.model.user_type == user_type)
        if tenant_id is not None:
            filters.append(self.model.tenant_id == tenant_id)
        if is_active is not None:
            filters.append(self.model.is_active == is_active)
            
        # 应用过滤条件
        if filters:
            query = query.filter(and_(*filters))
            
        return query.offset(skip).limit(limit).all()

user = CRUDUser(User) 
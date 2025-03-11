from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
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
            is_superuser=obj_in.is_superuser,
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


user = CRUDUser(User) 
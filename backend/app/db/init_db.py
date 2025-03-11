from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

def init_db(db: Session) -> None:
    # 创建超级管理员
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            username="admin",
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        
    # 建议添加：初始化基础数据
    # 例如：简历库类型、面试状态等基础数据
    # TODO: 根据业务需求添加其他初始化数据 
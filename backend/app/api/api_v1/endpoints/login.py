import logging
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.logging_config import setup_logger

# 配置日志
logger = setup_logger(__name__)

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        # 添加密码信息的日志
        logger.debug(f"Login attempt - Username: {form_data.username}")
        logger.debug(
            f"Password received (first 4 chars): "
            f"{form_data.password[:4]}..."
        )
        
        # 获取用户信息并记录日志
        user_in_db = crud.user.get_by_email(db, email=form_data.username)
        if user_in_db:
            logger.debug(f"User found in DB - Email: {user_in_db.email}")
            logger.debug(
                f"Stored password hash (first 10 chars): "
                f"{user_in_db.hashed_password[:10]}..."
            )
        else:
            logger.debug("No user found with this email")
        
        # 验证用户凭据
        user = crud.user.authenticate(
            db, email=form_data.username, password=form_data.password
        )
        
        if not user:
            logger.warning(
                f"Authentication failed for user: {form_data.username}"
            )
            raise HTTPException(
                status_code=400, detail="Incorrect email or password"
            )
            
        logger.debug(f"User authenticated successfully: {user.email}")
        
        # 检查用户状态
        if not crud.user.is_active(user):
            logger.warning(f"Inactive user attempted login: {user.email}")
            raise HTTPException(status_code=400, detail="Inactive user")
            
        # 生成访问令牌
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        logger.debug(f"Access token generated for user: {user.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise 
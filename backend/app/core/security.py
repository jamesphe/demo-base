from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging
from app.core.logging_config import setup_logger

# 配置日志
logger = setup_logger(__name__)

# 添加错误处理
logging.getLogger("passlib").setLevel(logging.ERROR)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT相关配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def reset_admin_password() -> str:
    """
    重置管理员密码并返回新的哈希值
    """
    password = "admin"
    # 使用相同的配置生成新的哈希
    new_hash = pwd_context.hash(password)
    logger.debug(f"Generated new hash for admin: {new_hash}")
    
    # 验证新哈希
    verify_result = pwd_context.verify(password, new_hash)
    logger.debug(f"Verification test result: {verify_result}")
    
    return new_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password) 
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging
from app.core.logging_config import setup_logger

# 配置日志
logger = setup_logger(__name__)

# 添加错误处理
logging.getLogger("passlib").setLevel(logging.ERROR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
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
    """
    验证密码
    """
    logger.debug(f"Verifying password - Plain: '{plain_password}'")
    logger.debug(f"Against hash: '{hashed_password}'")
    
    # 验证密码
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Verification result: {result}")
        
        if not result:
            # 如果验证失败，检查密码格式
            logger.debug(f"Password bytes: {plain_password.encode('utf-8').hex()}")
            logger.debug(f"Hash format: {hashed_password.split('$')}")
            
        return result
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    logger.debug(f"Generating hash for password: '{password}'")
    hashed = pwd_context.hash(password)
    logger.debug(f"Generated hash: '{hashed}'")
    
    # 立即验证新生成的哈希
    verify_result = pwd_context.verify(password, hashed)
    logger.debug(f"Immediate verification result: {verify_result}")
    return hashed 
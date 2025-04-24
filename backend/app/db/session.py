from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import redis
from typing import Generator

# 使用环境变量中的数据库配置
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,               # 增加连接池大小
    max_overflow=30,            # 增加最大溢出连接数
    pool_timeout=30,            # 设置连接超时
    pool_recycle=1800,         # 定期回收连接
    pool_pre_ping=True         # 自动检测断开的连接
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Redis连接
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    decode_responses=False
)

def get_db() -> Generator:
    """
    获取数据库会话
    
    Yields:
        数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
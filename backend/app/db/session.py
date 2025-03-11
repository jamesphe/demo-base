from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 建议添加数据库连接池配置
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    # 建议添加以下配置
    pool_size=5,  # 连接池大小
    max_overflow=10,  # 超过连接池大小外最多创建的连接数
    pool_timeout=30,  # 池中没有连接时等待的秒数
    pool_recycle=1800,  # 连接重置周期
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
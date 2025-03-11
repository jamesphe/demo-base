from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class ResumeRepository(Base):
    __tablename__ = "resume_repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    resume_type = Column(String(20), default="general", nullable=False)
    description = Column(Text)
    
    # 处理状态相关字段
    processing_status = Column(String(20), default="pending")
    processing_message = Column(String(200))
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(String(500))
    
    # 时间戳
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # 关系
    resumes = relationship("Resume", back_populates="repository") 
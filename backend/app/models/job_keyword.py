from sqlalchemy import (
    Column, Integer, String, DateTime, 
    ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class JobKeyword(Base):
    """职位匹配关键字模型"""
    __tablename__ = "job_keywords"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    sync_email_id = Column(
        Integer, 
        ForeignKey("resume_sync_emails.id"), 
        nullable=False
    )
    keyword = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    description = Column(Text)

    # 关联关系
    job = relationship("Job", back_populates="keywords")
    sync_email = relationship("ResumeSyncEmail", back_populates="keywords") 
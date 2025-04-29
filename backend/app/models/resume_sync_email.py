from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class ResumeSyncEmail(Base):
    """简历同步邮箱配置模型"""
    __tablename__ = "resume_sync_emails"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # 加密存储
    imap_server = Column(String(255), nullable=False)
    imap_port = Column(Integer, default=993)
    smtp_server = Column(String(255), nullable=False)
    smtp_port = Column(Integer, default=465)
    is_active = Column(Boolean, default=True)
    last_sync_time = Column(DateTime)
    sync_interval = Column(Integer, default=15)  # 同步间隔(分钟)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text)

    # 关联关系
    tenant = relationship("Tenant", back_populates="resume_sync_emails")
    keywords = relationship("JobKeyword", back_populates="sync_email") 
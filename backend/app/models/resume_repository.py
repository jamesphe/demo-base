from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class ResumeRepository(Base):
    """简历库模型"""
    __tablename__ = "resume_repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    resume_type = Column(String(50), default="general", nullable=False)
    description = Column(Text, nullable=True)
    
    # 修改租户ID字段定义，确保表名正确
    tenant_id = Column(
        Integer, 
        ForeignKey("tenant.id", ondelete="CASCADE"),  # 注意这里是 tenant 而不是 tenants
        nullable=False,
        index=True
    )
    
    # 处理状态相关字段
    processing_status = Column(String(20), default="pending")
    processing_message = Column(String(200))
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(String(500))
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 关系
    tenant = relationship("Tenant", back_populates="resume_repositories")
    resumes = relationship("Resume", back_populates="repository")

    def __repr__(self):
        return f"<ResumeRepository {self.name}>" 
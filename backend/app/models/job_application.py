from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class JobApplication(Base):
    """职位申请记录表"""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    status = Column(
        Enum(
            "pending",
            "reviewed",
            "interviewed",
            "offered",
            "rejected",
            "withdrawn",
            name="application_status"
        ),
        default="pending"
    )
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # 恢复重要的业务字段
    apply_time = Column(DateTime, default=datetime.utcnow)
    review_time = Column(DateTime)
    review_notes = Column(Text)
    
    # 添加租户ID字段
    tenant_id = Column(Integer, ForeignKey("tenant.id"))
    
    # 关联关系
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    creator = relationship("User", foreign_keys=[created_by])
    tenant = relationship("Tenant") 
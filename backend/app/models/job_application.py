from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum, String, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class JobApplication(Base):
    """职位申请记录表"""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(
            "pending",
            "reviewed",
            "interview_scheduled",
            "interviewed",
            "offered",
            "rejected",
            "withdrawn",
            name="application_status"
        ),
        default="pending"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # 恢复重要的业务字段
    apply_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    review_time = Column(DateTime)
    review_notes = Column(Text)
    
    # 添加匹配度和匹配理由字段
    match_score = Column(Float, default=0.0)  # 匹配度评分
    match_reason = Column(Text)  # 匹配理由
    
    # 关联关系
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    tenant = relationship("Tenant", back_populates="applications")
    
    # 修改这一行，使用backref而不是back_populates
    creator = relationship(
        "User", 
        foreign_keys=[created_by],
        backref="created_applications"
    )

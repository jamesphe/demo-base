from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class JobApplication(Base):
    """职位申请记录表"""
    __tablename__ = "job_application"

    application_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
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
    apply_time = Column(DateTime, default=datetime.utcnow)
    review_time = Column(DateTime)
    review_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications") 
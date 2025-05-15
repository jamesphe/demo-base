from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from .interview_interviewer import interview_interviewers


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    tenant_id = Column(Integer, ForeignKey("tenant.id"))
    status = Column(String(50))  # 待安排、已安排、已完成、已取消
    schedule_time = Column(DateTime)
    duration = Column(Integer, default=60)  # 面试时长，单位为分钟
    location = Column(String(255), nullable=True)  # 面试地点
    # 面试类型：first(初试)、second(复试)、final(终试)
    interview_type = Column(String(50), default="first")
    notes = Column(String(1000), nullable=True)  # 面试备注
    feedback = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    resume = relationship("Resume", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    interviewers = relationship(
        "User", 
        secondary=interview_interviewers,
        backref="interview_participations"
    ) 
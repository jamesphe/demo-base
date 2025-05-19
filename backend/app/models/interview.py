from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Float, Text
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from .interview_interviewer import interview_interviewers


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    # 主面试官
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"))
    # 注意: candidate_id 字段在数据库中不存在，已移除引用
    # 通过 resume.talent_id 关联候选人
    status = Column(String(50))  # 待安排、已安排、已完成、已取消、已评估
    schedule_time = Column(DateTime)
    duration = Column(Integer, default=60)  # 面试时长，单位为分钟
    location = Column(String(255), nullable=True)  # 面试地点
    # 面试类型：first(初试)、second(复试)、final(终试)
    interview_type = Column(String(50), default="first")
    notes = Column(Text, nullable=True)  # 面试备注
    feedback = Column(String(1000), nullable=True)
    
    # 评估相关字段
    evaluation_score = Column(Float, nullable=True)  # 面试评估总分
    status_updated_at = Column(DateTime, nullable=True)  # 状态更新时间
    completed_at = Column(DateTime, nullable=True)  # 面试完成时间
    evaluated_at = Column(DateTime, nullable=True)  # 评估完成时间
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 关系
    resume = relationship("Resume", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    # 移除已废弃的Candidate关系
    # candidate = relationship("Candidate", back_populates="interviews")
    interviewers = relationship(
        "User", 
        secondary=interview_interviewers,
        backref="interview_participations"
    )
    evaluation = relationship(
        "InterviewEvaluation", 
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan"
    )
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        backref="created_interviews"
    ) 
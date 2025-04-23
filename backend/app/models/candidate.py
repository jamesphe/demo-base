from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    resume_url = Column(String(255))
    status = Column(String(50))  # 如: 待筛选、初筛通过、面试中等
    notes = Column(Text, nullable=True)  # 备注信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate")
    resumes = relationship(
        "Resume", 
        back_populates="candidate", 
        foreign_keys="[Resume.candidate_id]"
    )
    
    # 添加职位关联
    job_id = Column(Integer, ForeignKey("jobs.id"))
    job = relationship("Job", back_populates="candidates")
    
    # 添加简历ID关联
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    primary_resume = relationship(
        "Resume", 
        foreign_keys=[resume_id],
        backref="primary_for_candidate"
    )
 
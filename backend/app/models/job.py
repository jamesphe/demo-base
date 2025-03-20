from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.job_requirement import JobRequiredSkill, JobRequiredCertification

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    job_type = Column(String(50), nullable=False)
    headcount = Column(Integer, default=1)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_type = Column(Enum("日薪", "月薪", "年薪", name="salary_type"), nullable=False)
    location = Column(String(255), nullable=False)
    experience_required = Column(String(50))
    education_required = Column(String(50))
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    benefits = Column(Text)
    status = Column(
        Enum("draft", "published", "closed", name="job_status"),
        default="draft"
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    closed_at = Column(DateTime)

    # 关联
    tenant = relationship("Tenant", back_populates="jobs")
    publisher = relationship(
        "User",
        back_populates="published_jobs",
        foreign_keys=[publisher_id]
    )
    candidates = relationship("Candidate", back_populates="job")
    required_skills = relationship("JobRequiredSkill", back_populates="job")
    required_certifications = relationship("JobRequiredCertification", back_populates="job")
    applications = relationship("JobApplication", back_populates="job")
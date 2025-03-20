from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class JobRequiredSkill(Base):
    """职位-技能要求关联表"""
    __tablename__ = "job_required_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_level = Column(String(50), nullable=False)
    is_required = Column(Boolean, default=True)

    # 关联
    job = relationship("Job", back_populates="required_skills")
    skill = relationship("Skill", back_populates="job_requirements")


class JobRequiredCertification(Base):
    """职位-证书要求关联表"""
    __tablename__ = "job_required_certifications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    is_required = Column(Boolean, default=True)

    # 关联
    job = relationship("Job", back_populates="required_certifications")
    certification = relationship("Certification", back_populates="job_requirements") 
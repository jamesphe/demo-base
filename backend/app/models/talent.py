from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    Enum, Text, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class Talent(Base):
    __tablename__ = "talent"

    talent_id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=True)
    name = Column(String(100), nullable=False)
    gender = Column(Enum('M', 'F', name='gender_type'), default='M')
    birth_date = Column(Date)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    address = Column(String(255))
    id_number = Column(String(50))
    registration_date = Column(DateTime, default=datetime.utcnow)
    verified_status = Column(Boolean, default=False)
    profile_picture = Column(String(255))
    profile_summary = Column(Text)
    primary_job_type = Column(String(50))
    job_location_preference = Column(String(100))
    expected_salary = Column(String(50))
    data_source = Column(
        Enum('个人用户', '技术学校', '人力公司', '租户自建', name='data_source_type'),
        default='个人用户'
    )

    # 关联关系
    tenant = relationship("Tenant", back_populates="talents")
    certifications = relationship(
        "CandidateCertification",
        back_populates="talent"
    )
    education = relationship("CandidateEducation", back_populates="talent")
    experience = relationship("CandidateExperience", back_populates="talent")
    skills = relationship("TalentSkill", back_populates="talent")
    resumes = relationship(
        "Resume",
        back_populates="talent",
        foreign_keys="[Resume.talent_id]"
    )
    pool_memberships = relationship(
        "TalentPoolMember",
        back_populates="talent"
    ) 
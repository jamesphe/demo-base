from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(Integer, primary_key=True, index=True)
    tenant_name = Column(String(100), nullable=False, unique=True)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    external_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(
        Enum('active', 'inactive', name='tenant_status'),
        default='active'
    )

    # 关联关系
    users = relationship("User", back_populates="tenant")
    candidates = relationship("Candidate", back_populates="tenant")
    talents = relationship("Talent", back_populates="tenant")
    notifications = relationship("Notification", back_populates="tenant")
    talent_pools = relationship("TalentPool", back_populates="tenant")
    resumes = relationship("Resume", back_populates="tenant")
    jobs = relationship("Job", back_populates="tenant")
    skills = relationship("Skill", back_populates="tenant")
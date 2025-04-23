from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
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

    # 企业微信相关字段
    qywx_corp_id = Column(String(100), comment='企业微信CorpID')
    qywx_permanent_code = Column(String(512), comment='企业微信永久授权码')
    qywx_agent_id = Column(Integer, comment='企业微信应用AgentID')
    auth_user_id = Column(String(100), comment='授权管理员UserId')
    auth_time = Column(DateTime, comment='授权时间')
    expiry_time = Column(DateTime, comment='授权过期时间')
    subscription_type = Column(String(50), default='trial', comment='订阅类型: trial, basic, premium')
    subscription_start = Column(DateTime, comment='订阅开始时间')
    subscription_end = Column(DateTime, comment='订阅结束时间')

    # 关联关系
    users = relationship("User", back_populates="tenant")
    candidates = relationship("Candidate", back_populates="tenant")
    talents = relationship("Talent", back_populates="tenant")
    notifications = relationship("Notification", back_populates="tenant")
    talent_pools = relationship("TalentPool", back_populates="tenant")
    resumes = relationship("Resume", back_populates="tenant")
    jobs = relationship("Job", back_populates="tenant")
    skills = relationship("Skill", back_populates="tenant")
    certifications = relationship("Certification", back_populates="tenant")
    applications = relationship("JobApplication", back_populates="tenant")
    resume_repositories = relationship(
        "ResumeRepository", 
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    auth_events = relationship("QywxAuthEvents", back_populates="tenant")
    transactions = relationship("SubscriptionTransaction", back_populates="tenant")
    api_quotas = relationship("ApiQuota", back_populates="tenant")
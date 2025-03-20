from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)  # NULL表示平台公共技能
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(
        Enum("active", "inactive", name="skill_status"),
        default="active"
    )

    # 关联关系
    tenant = relationship("Tenant", back_populates="skills")
    talents = relationship("TalentSkill", back_populates="skill")
    job_requirements = relationship("JobRequiredSkill", back_populates="skill")

    __table_args__ = (
        # 确保同一租户下技能名称唯一
        UniqueConstraint('tenant_id', 'name', name='uk_tenant_skill'),
    ) 
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    # NULL表示平台公共证书
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)  
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    issuing_organization = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    status = Column(
        Enum("active", "inactive", name="certification_status"),
        default="active"
    )

    # 关联关系
    tenant = relationship("Tenant", back_populates="certifications")
    job_requirements = relationship(
        "JobRequiredCertification", back_populates="certification"
    )
    talent_certifications = relationship(
        "TalentCertification", back_populates="certification_type"
    )

    __table_args__ = (
        # 确保同一租户下证书名称唯一
        UniqueConstraint('tenant_id', 'name', name='uk_tenant_certification'),
    ) 
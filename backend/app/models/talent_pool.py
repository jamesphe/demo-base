from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class TalentPool(Base):
    __tablename__ = "talent_pool"

    pool_id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(
        Integer,
        ForeignKey("tenant.id"),
        nullable=False
    )
    pool_name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关联关系
    tenant = relationship("Tenant", back_populates="talent_pools")
    members = relationship("TalentPoolMember", back_populates="pool")


class TalentPoolMember(Base):
    __tablename__ = "talent_pool_member"

    member_id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(
        Integer,
        ForeignKey("talent_pool.pool_id"),
        nullable=False
    )
    talent_id = Column(
        Integer,
        ForeignKey("talent.talent_id"),
        nullable=False
    )
    remark = Column(String(255))
    added_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # 关联关系
    pool = relationship("TalentPool", back_populates="members")
    talent = relationship("Talent", back_populates="pool_memberships") 
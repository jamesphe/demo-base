from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime


class ApiQuota(Base):
    """API访问限额表"""
    
    __tablename__ = "api_quota"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    api_name = Column(String(100), nullable=False)
    daily_limit = Column(Integer, default=1000)
    monthly_limit = Column(Integer, default=20000)
    current_daily_usage = Column(Integer, default=0)
    current_monthly_usage = Column(Integer, default=0)
    last_reset_daily = Column(DateTime)
    last_reset_monthly = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="api_quotas")
    
    # 租户+API名称唯一约束
    __table_args__ = (
        UniqueConstraint("tenant_id", "api_name", name="uk_tenant_api"),
    ) 
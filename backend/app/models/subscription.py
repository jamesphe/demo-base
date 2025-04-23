from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime


class SubscriptionPlan(Base):
    """订阅计划表"""
    
    __tablename__ = "subscription_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_type = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)
    duration_unit = Column(
        Enum("day", "month", "year", name="duration_unit_enum"), 
        nullable=False
    )
    features = Column(String(1000))
    is_active = Column(
        Enum("active", "inactive", name="plan_status_enum"), 
        default="active"
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SubscriptionTransaction(Base):
    """订阅交易记录表"""
    
    __tablename__ = "subscription_transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    plan_type = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(
        Enum(
            "pending", "paid", "failed", "refunded", "free", 
            name="payment_status_enum"
        ),
        default="pending"
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    transaction_time = Column(DateTime, default=datetime.now)
    payment_time = Column(DateTime)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    remark = Column(String(255))
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="transactions") 
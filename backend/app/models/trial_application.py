from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TrialApplication(Base):
    __tablename__ = "trial_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    contact_email = Column(String(255), nullable=False)
    
    # 添加新字段
    company_size = Column(String(50))
    business_description = Column(Text)
    application_reason = Column(Text)
    
    status = Column(String(20), default="pending")
    reject_reason = Column(Text)
    trial_start_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 简化关系定义
    user = relationship("User", back_populates="trial_applications") 
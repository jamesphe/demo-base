from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class QywxAuthEvents(Base):
    __tablename__ = "qywx_auth_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"))
    qywx_corp_id = Column(String(100))
    event_type = Column(String(50))
    event_time = Column(DateTime, default=datetime.now)
    event_data = Column(JSON)
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="auth_events") 
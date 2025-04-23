from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base_class import Base
from datetime import datetime


class QywxSuiteTicket(Base):
    """企业微信Suite Ticket存储表"""
    
    __tablename__ = "qywx_suite_ticket"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    suite_id = Column(String(100), unique=True, nullable=False, index=True)
    ticket = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) 
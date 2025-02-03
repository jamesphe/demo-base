from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.db.base_class import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    requirements = Column(Text)
    salary_range = Column(String(100))
    location = Column(String(255))
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    ) 
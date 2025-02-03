from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    resume_url = Column(String(255))
    status = Column(String(50))  # 如: 待筛选、初筛通过、面试中等
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # 关联关系
    interviews = relationship("Interview", back_populates="candidate") 
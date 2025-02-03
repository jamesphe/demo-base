from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    interviewer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50))  # 待安排、已安排、已完成、已取消
    schedule_time = Column(DateTime)
    feedback = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User") 
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TalentExperience(Base):
    __tablename__ = "talent_experience"

    experience_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talent.talent_id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    job_description = Column(Text)
    achievements = Column(Text)
    attachment_url = Column(String(255))

    # 关联关系
    talent = relationship("Talent", back_populates="experience") 
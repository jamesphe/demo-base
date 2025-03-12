from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    education_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talent.talent_id"), nullable=False)
    institution_name = Column(String(255), nullable=False)
    degree = Column(String(100))
    field_of_study = Column(String(100))
    start_date = Column(Date)
    graduation_date = Column(Date)
    certificate_url = Column(String(255))
    description = Column(Text)

    # 关联关系
    talent = relationship("Talent", back_populates="education") 
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Skill(Base):
    __tablename__ = "skill"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), nullable=False)
    skill_description = Column(Text)
    category = Column(String(50))

    # 关联关系
    talents = relationship("TalentSkill", back_populates="skill") 
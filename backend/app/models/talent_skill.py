from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TalentSkill(Base):
    __tablename__ = "talent_skill"

    talent_skill_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talent.talent_id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), nullable=False)

    # 关联关系
    talent = relationship("Talent", back_populates="skills")
    skill = relationship("Skill", back_populates="talents") 
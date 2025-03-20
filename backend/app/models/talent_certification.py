from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TalentCertification(Base):
    __tablename__ = "talent_certification"

    certification_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talent.talent_id"), nullable=False)
    certification_type_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    certification_name = Column(String(100), nullable=False)
    issuing_organization = Column(String(100))
    issue_date = Column(Date)
    expiration_date = Column(Date)
    document_url = Column(String(255))

    # 关联关系
    talent = relationship("Talent", back_populates="certifications")
    certification_type = relationship("Certification", back_populates="talent_certifications") 
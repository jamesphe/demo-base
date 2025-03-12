from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.candidate_certification import CandidateCertification
from app.schemas.certification import CertificationCreate, CertificationUpdate


class CertificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_certification(
        self,
        certification: CertificationCreate
    ) -> CandidateCertification:
        """创建认证信息"""
        db_certification = CandidateCertification(
            talent_id=certification.talent_id,
            certification_name=certification.certification_name,
            issuing_organization=certification.issuing_organization,
            issue_date=certification.issue_date,
            expiration_date=certification.expiration_date,
            document_url=certification.document_url
        )
        self.db.add(db_certification)
        self.db.commit()
        self.db.refresh(db_certification)
        return db_certification
    
    def get_certification(
        self,
        certification_id: int
    ) -> Optional[CandidateCertification]:
        """获取单个认证详情"""
        query = self.db.query(CandidateCertification)
        return (query.filter(
            CandidateCertification.certification_id == certification_id
        ).first())
    
    def list_talent_certifications(
        self,
        talent_id: int
    ) -> List[CandidateCertification]:
        """获取人才的所有认证"""
        return (self.db.query(CandidateCertification)
                .filter(CandidateCertification.talent_id == talent_id)
                .all())
    
    def update_certification(
        self,
        certification_id: int,
        certification: CertificationUpdate
    ) -> Optional[CandidateCertification]:
        """更新认证信息"""
        db_certification = self.get_certification(certification_id)
        if not db_certification:
            return None
            
        update_data = certification.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_certification, field, value)
            
        self.db.commit()
        self.db.refresh(db_certification)
        return db_certification
    
    def delete_certification(self, certification_id: int) -> bool:
        """删除认证信息"""
        db_certification = self.get_certification(certification_id)
        if not db_certification:
            return False
            
        self.db.delete(db_certification)
        self.db.commit()
        return True 
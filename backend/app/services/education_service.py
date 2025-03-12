from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.candidate_education import CandidateEducation
from app.schemas.education import EducationCreate, EducationUpdate


class EducationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_education(
        self,
        education: EducationCreate
    ) -> CandidateEducation:
        """创建教育经历"""
        db_education = CandidateEducation(
            talent_id=education.talent_id,
            institution_name=education.institution_name,
            degree=education.degree,
            field_of_study=education.field_of_study,
            start_date=education.start_date,
            graduation_date=education.graduation_date,
            certificate_url=education.certificate_url,
            description=education.description
        )
        self.db.add(db_education)
        self.db.commit()
        self.db.refresh(db_education)
        return db_education
    
    def get_education(
        self,
        education_id: int
    ) -> Optional[CandidateEducation]:
        """获取单个教育经历"""
        return (self.db.query(CandidateEducation)
                .filter(CandidateEducation.education_id == education_id)
                .first())
    
    def list_talent_educations(
        self,
        talent_id: int
    ) -> List[CandidateEducation]:
        """获取人才的所有教育经历"""
        return (self.db.query(CandidateEducation)
                .filter(CandidateEducation.talent_id == talent_id)
                .all())
    
    def update_education(
        self,
        education_id: int,
        education: EducationUpdate
    ) -> Optional[CandidateEducation]:
        """更新教育经历"""
        db_education = self.get_education(education_id)
        if not db_education:
            return None
            
        update_data = education.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_education, field, value)
            
        self.db.commit()
        self.db.refresh(db_education)
        return db_education
    
    def delete_education(self, education_id: int) -> bool:
        """删除教育经历"""
        db_education = self.get_education(education_id)
        if not db_education:
            return False
            
        self.db.delete(db_education)
        self.db.commit()
        return True 
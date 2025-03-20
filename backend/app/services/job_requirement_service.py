from typing import List
from sqlalchemy.orm import Session
from app import crud, models
from app.schemas.job_requirement import (
    JobRequiredSkillCreate,
    JobRequiredCertificationCreate
)


class JobRequirementService:
    def __init__(self, db: Session):
        self.db = db

    def add_job_skills(
        self,
        job_id: int,
        skills: List[JobRequiredSkillCreate]
    ) -> List[models.JobRequiredSkill]:
        """添加职位技能要求"""
        result = []
        for skill in skills:
            skill_obj = crud.job_required_skill.create(
                self.db,
                obj_in=skill
            )
            result.append(skill_obj)
        return result

    def update_job_skills(
        self,
        job_id: int,
        skills: List[JobRequiredSkillCreate]
    ) -> List[models.JobRequiredSkill]:
        """更新职位技能要求"""
        # 删除原有技能要求
        existing_skills = crud.job_required_skill.get_by_job(
            self.db,
            job_id=job_id
        )
        for skill in existing_skills:
            crud.job_required_skill.remove(
                self.db,
                id=skill.job_skill_id
            )
        
        # 添加新的技能要求
        return self.add_job_skills(job_id, skills)

    def add_job_certifications(
        self,
        job_id: int,
        certifications: List[JobRequiredCertificationCreate]
    ) -> List[models.JobRequiredCertification]:
        """添加职位证书要求"""
        result = []
        for cert in certifications:
            cert_obj = crud.job_required_certification.create(
                self.db,
                obj_in=cert
            )
            result.append(cert_obj)
        return result

    def update_job_certifications(
        self,
        job_id: int,
        certifications: List[JobRequiredCertificationCreate]
    ) -> List[models.JobRequiredCertification]:
        """更新职位证书要求"""
        # 删除原有证书要求
        existing_certs = crud.job_required_certification.get_by_job(
            self.db,
            job_id=job_id
        )
        for cert in existing_certs:
            crud.job_required_certification.remove(
                self.db,
                id=cert.job_cert_id
            )
        
        # 添加新的证书要求
        return self.add_job_certifications(job_id, certifications)

    def get_job_requirements(
        self,
        job_id: int
    ) -> dict:
        """获取职位的所有要求(技能和证书)"""
        skills = crud.job_required_skill.get_by_job(
            self.db,
            job_id=job_id
        )
        certifications = crud.job_required_certification.get_by_job(
            self.db,
            job_id=job_id
        )
        return {
            "skills": skills,
            "certifications": certifications
        } 
from typing import Optional
from pydantic import BaseModel, Field


class JobRequiredSkillBase(BaseModel):
    """职位技能要求基础模型"""
    skill_id: int = Field(..., description="技能ID")
    is_required: bool = Field(default=True, description="是否必需技能")


class JobRequiredSkillCreate(JobRequiredSkillBase):
    """创建职位技能要求"""
    pass


class JobRequiredSkill(JobRequiredSkillBase):
    """职位技能要求完整模型"""
    job_skill_id: int
    job_id: int
    skill_name: str  # 用于展示

    class Config:
        from_attributes = True


class JobRequiredCertificationBase(BaseModel):
    """职位证书要求基础模型"""
    certification_name: str = Field(..., description="证书名称")
    is_required: bool = Field(default=True, description="是否必需证书")


class JobRequiredCertificationCreate(JobRequiredCertificationBase):
    """创建职位证书要求"""
    pass


class JobRequiredCertification(JobRequiredCertificationBase):
    """职位证书要求完整模型"""
    job_cert_id: int
    job_id: int

    class Config:
        from_attributes = True 
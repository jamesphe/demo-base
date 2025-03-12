from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ResumeBase(BaseModel):
    resume_id: Optional[str] = None
    repository_id: Optional[int] = None
    resume_type: Optional[str] = "general"
    tenant_id: Optional[int] = None
    
    # 文件信息
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    content: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    
    # 个人基本信息
    name: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # 个人状态信息
    political_status: Optional[str] = None
    marital_status: Optional[str] = None
    hukou: Optional[str] = None
    current_address: Optional[str] = None
    
    # 教育信息
    highest_education: Optional[str] = None
    highest_degree: Optional[str] = None
    is_normal_major: Optional[bool] = False
    major: Optional[str] = None
    graduate_school: Optional[str] = None
    graduation_date: Optional[datetime] = None
    is_fulltime: Optional[bool] = True
    
    # 教师资格相关
    has_teacher_cert: Optional[bool] = False
    cert_id: Optional[str] = None
    cert_stage: Optional[str] = None
    cert_subject: Optional[str] = None
    cert_obtained_date: Optional[datetime] = None
    mandarin_level: Optional[str] = None
    is_official_staff: Optional[bool] = False
    
    # 工作经验
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    current_salary: Optional[str] = None
    industry: Optional[str] = None
    work_history: Optional[List[Dict[str, Any]]] = None
    
    # 求职意向
    expected_industry: Optional[str] = None
    expected_position: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    expected_location: Optional[str] = None
    job_status: Optional[str] = None
    
    # 技能与证书
    skills: Optional[List[Dict[str, Any]]] = None
    certificates: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    computer_skills: Optional[List[Dict[str, Any]]] = None
    
    # 项目经验
    project_experience: Optional[List[Dict[str, Any]]] = None
    
    # 其他信息
    self_evaluation: Optional[str] = None
    hobbies: Optional[str] = None
    awards: Optional[str] = None
    summary: Optional[str] = None
    
    processing_status: Optional[str] = "pending"
    processing_message: Optional[str] = None


class ResumeCreate(BaseModel):
    resume_id: str
    repository_id: int
    tenant_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: str
    processing_status: str = "pending"
    created_at: datetime = datetime.utcnow()


class ResumeUpdate(BaseModel):
    content: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    processing_status: Optional[str] = None
    processing_message: Optional[str] = None
    processing_error: Optional[str] = None
    talent_id: Optional[int] = None
    
    # 可选的个人信息字段
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    highest_education: Optional[str] = None
    major: Optional[str] = None
    graduate_school: Optional[str] = None
    skills: Optional[list] = None


class ResumeInDBBase(ResumeBase):
    id: int
    resume_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Resume(ResumeInDBBase):
    pass


# 用于返回简要信息的模型
class ResumeBasicInfo(BaseModel):
    id: int
    resume_id: str
    file_name: str
    resume_type: str
    processing_status: str
    name: Optional[str] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    } 
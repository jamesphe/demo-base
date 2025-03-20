from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, 
    JSON, Enum, Boolean
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime


class Resume(Base):
    """简历模型"""
    __tablename__ = "resumes"

    # 基本信息
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(String(100), unique=True, index=True)
    
    # 文件信息
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, doc, docx
    resume_type = Column(String(20), default="general")
    content = Column(Text)
    parsed_data = Column(JSON)
    
    # 处理状态
    processing_status = Column(
        String(20), 
        default="pending"
    )  # pending, processing, completed, failed
    processing_message = Column(String(200))
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)
    
    # 个人基本信息
    name = Column(String(100))
    gender = Column(String(10))
    birthdate = Column(DateTime)
    id_number = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    stature = Column(String(20))
    weight = Column(String(20))
    nation = Column(String(50))
    english_level = Column(String(50))
    city = Column(String(100))
    district = Column(String(100))
    
    # 个人状态信息
    political_status = Column(String(50))
    marital_status = Column(String(20))
    hukou = Column(String(100))
    current_address = Column(String(255))
    
    # 教育信息
    highest_education = Column(String(50))
    highest_degree = Column(String(50))
    major = Column(String(100))
    graduate_school = Column(String(100))
    graduation_date = Column(DateTime)
    
    # 工作经验
    experience_years = Column(Integer)
    current_company = Column(String(100))
    current_position = Column(String(100))
    current_salary = Column(String(50))
    work_time = Column(String(50))
    work_history = Column(JSON)
    
    # 求职意向
    expected_position = Column(String(100))
    expected_salary = Column(String(50))
    expected_location = Column(String(100))
    
    # 技能与证书
    skills = Column(JSON)
    certificates = Column(JSON)
    
    # 匹配状态
    matching_status = Column(
        Enum('待匹配', '已匹配', '待确认', '新人才', name='matching_status_type'),
        default='待匹配'
    )
    matching_score = Column(Integer)  # 职位匹配度评分
    
    # 版本信息
    resume_version = Column(Integer, default=1)  # 同一人才的简历版本
    is_latest = Column(Boolean, default=True)  # 是否为最新版本
    
    # 来源信息
    source_channel = Column(String(50))  # 如：官网、猎聘、智联等
    source_batch = Column(String(100))  # 批次号，用于追踪批量导入
    
    # 质量评分
    completeness_score = Column(Integer)  # 信息完整度评分
    
    # 时间戳
    created_at = Column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关联关系
    repository_id = Column(Integer, ForeignKey("resume_repositories.id"))
    repository = relationship("ResumeRepository", back_populates="resumes")
    
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)
    candidate = relationship("Candidate", back_populates="resumes")
    
    talent_id = Column(Integer, ForeignKey("talent.talent_id"))
    talent = relationship("Talent", back_populates="resumes")
    
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)
    tenant = relationship("Tenant")
    
    # 职称信息
    talent_name = Column(String(100))
    talent_team = Column(String(100))
    talent_type = Column(String(100))
    title_rank = Column(String(100))
    
    # 经历信息
    edu_experience = Column(JSON)
    awards = Column(JSON)
    
    # 其他信息
    family_situation = Column(String(255))
    
    # 其他信息
    other_info = Column(String(255))

    # 添加关联关系
    applications = relationship("JobApplication", back_populates="resume") 
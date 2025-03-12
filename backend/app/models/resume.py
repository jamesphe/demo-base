from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(String(100), unique=True, index=True)
    
    # 基本文件信息
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, doc, docx
    resume_type = Column(String(20), default="general")
    content = Column(Text)
    parsed_data = Column(JSON, nullable=True)
    
    # 处理状态相关字段
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
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
    work_history = Column(JSON)
    
    # 求职意向
    expected_position = Column(String(100))
    expected_salary = Column(String(50))
    expected_location = Column(String(100))
    
    # 技能与证书
    skills = Column(JSON)
    certificates = Column(JSON)
    
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

    # 关联关系
    repository = relationship("ResumeRepository", back_populates="resumes")
    candidate = relationship("Candidate", back_populates="resumes")
    talent = relationship("Talent", back_populates="resumes")

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=True) 
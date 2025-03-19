from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """职位基础模型"""
    title: str = Field(..., description="职位标题", max_length=100)
    job_type: str = Field(..., description="工种类型", max_length=50)
    headcount: int = Field(default=1, description="招聘人数")
    salary_min: float = Field(..., description="薪资范围最小值")
    salary_max: float = Field(..., description="薪资范围最大值")
    salary_type: str = Field(..., description="薪资类型(日薪/月薪/年薪)")
    location: str = Field(..., description="工作地点", max_length=255)
    experience_required: Optional[str] = Field(None, description="要求工作经验", max_length=50)
    education_required: Optional[str] = Field(None, description="学历要求", max_length=50)
    description: str = Field(..., description="职位描述")
    requirements: Optional[str] = Field(None, description="岗位要求")
    benefits: Optional[str] = Field(None, description="福利待遇")


class JobCreate(JobBase):
    """创建职位的请求模型"""
    title: str
    job_type: str
    headcount: int
    salary_min: int = 0
    salary_max: int = 0
    salary_type: str
    location: str
    experience_required: str
    education_required: str
    description: str
    requirements: str
    benefits: str


class JobUpdate(JobBase):
    """更新职位模型"""
    title: Optional[str] = Field(None, description="职位标题", max_length=100)
    job_type: Optional[str] = Field(None, description="工种类型", max_length=50)
    headcount: Optional[int] = Field(None, description="招聘人数")
    salary_min: Optional[float] = Field(None, description="薪资范围最小值")
    salary_max: Optional[float] = Field(None, description="薪资范围最大值")
    salary_type: Optional[str] = Field(None, description="薪资类型(日薪/月薪/年薪)")
    location: Optional[str] = Field(None, description="工作地点", max_length=255)
    status: Optional[str] = Field(None, description="职位状态(draft/published/closed)")


class Job(JobBase):
    """职位完整模型"""
    id: int
    tenant_id: int
    publisher_id: int
    status: str
    created_at: datetime
    published_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# 添加带有候选人数量的 Job Schema
class JobWithCandidateCount(Job):
    """带候选人数量的职位模型"""
    candidate_count: int = 0 
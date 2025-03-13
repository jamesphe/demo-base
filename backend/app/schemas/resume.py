from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class SkillInfo(BaseModel):
    """技能信息模型"""
    name: str = Field(..., description="技能名称")
    level: Optional[str] = Field(None, description="技能水平")
    description: Optional[str] = Field(None, description="技能描述")


class CertificateInfo(BaseModel):
    """证书信息模型"""
    name: str = Field(..., description="证书名称")
    issuer: Optional[str] = Field(None, description="发证机构")
    issue_date: Optional[datetime] = Field(None, description="发证日期")
    expire_date: Optional[datetime] = Field(None, description="过期日期")


class WorkHistoryInfo(BaseModel):
    """工作经历信息模型"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    start_date: datetime = Field(..., description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    description: Optional[str] = Field(None, description="工作描述")


class ResumeBase(BaseModel):
    """简历基础模型"""
    
    # 文件信息
    file_name: Optional[str] = Field(None, description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_type: Optional[str] = Field(None, description="文件类型")
    resume_type: Optional[str] = Field("general", description="简历类型")
    content: Optional[str] = Field(None, description="简历内容")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="解析数据")
    
    # 处理状态
    processing_status: Optional[str] = Field("pending", description="处理状态")
    processing_message: Optional[str] = Field(None, description="处理消息")
    processing_started_at: Optional[datetime] = Field(None, description="处理开始时间")
    processing_completed_at: Optional[datetime] = Field(None, description="处理完成时间")
    processing_error: Optional[str] = Field(None, description="处理错误信息")
    
    # 个人基本信息
    name: Optional[str] = Field(None, description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    birthdate: Optional[datetime] = Field(None, description="出生日期")
    id_number: Optional[str] = Field(None, description="身份证号")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    
    # 个人状态信息
    political_status: Optional[str] = Field(None, description="政治面貌")
    marital_status: Optional[str] = Field(None, description="婚姻状况")
    hukou: Optional[str] = Field(None, description="户口所在地")
    current_address: Optional[str] = Field(None, description="当前住址")
    
    # 教育信息
    highest_education: Optional[str] = Field(None, description="最高学历")
    highest_degree: Optional[str] = Field(None, description="最高学位")
    major: Optional[str] = Field(None, description="专业")
    graduate_school: Optional[str] = Field(None, description="毕业院校")
    graduation_date: Optional[datetime] = Field(None, description="毕业时间")
    
    # 工作经验
    experience_years: Optional[int] = Field(None, description="工作年限")
    current_company: Optional[str] = Field(None, description="当前公司")
    current_position: Optional[str] = Field(None, description="当前职位")
    current_salary: Optional[str] = Field(None, description="当前薪资")
    work_history: Optional[Dict[str, Any]] = Field(None, description="工作经历")
    
    # 求职意向
    expected_position: Optional[str] = Field(None, description="期望职位")
    expected_salary: Optional[str] = Field(None, description="期望薪资")
    expected_location: Optional[str] = Field(None, description="期望地点")
    
    # 技能与证书
    skills: Optional[Dict[str, Any]] = Field(None, description="技能列表")
    certificates: Optional[Dict[str, Any]] = Field(None, description="证书列表")
    
    # 匹配状态
    matching_status: Optional[str] = Field("待匹配", description="匹配状态")
    matching_score: Optional[int] = Field(None, description="匹配分数")
    
    # 版本信息
    resume_version: Optional[int] = Field(1, description="简历版本")
    is_latest: Optional[bool] = Field(True, description="是否最新版本")
    
    # 来源信息
    source_channel: Optional[str] = Field(None, description="来源渠道")
    source_batch: Optional[str] = Field(None, description="来源批次")
    
    # 质量评分
    completeness_score: Optional[int] = Field(None, description="完整度评分")
    
    # 添加关联关系字段
    repository_id: Optional[int] = Field(None, description="简历库ID")
    candidate_id: Optional[int] = Field(None, description="候选人ID")
    talent_id: Optional[int] = Field(None, description="人才ID")
    tenant_id: Optional[int] = Field(None, description="租户ID")

    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "name": "张三",
                "gender": "男",
                "phone": "13800138000",
                "email": "zhangsan@example.com"
            }
        }


class ResumeCreate(ResumeBase):
    """简历创建模型"""
    resume_id: str = Field(..., description="简历ID")
    repository_id: int = Field(..., description="简历库ID")
    tenant_id: Optional[int] = Field(None, description="租户ID")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")


class ResumeUpdate(ResumeBase):
    """简历更新模型"""
    pass


class Resume(ResumeBase):
    """简历完整模型"""
    id: int = Field(..., description="主键ID")
    resume_id: str = Field(..., description="简历ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class ResumeBasicInfo(BaseModel):
    """简历基本信息模型"""
    id: int = Field(..., description="主键ID")
    resume_id: str = Field(..., description="简历ID")
    file_name: str = Field(..., description="文件名")
    resume_type: str = Field(..., description="简历类型")
    processing_status: str = Field(..., description="处理状态")
    name: Optional[str] = Field(None, description="姓名")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = {
        "from_attributes": True
    } 
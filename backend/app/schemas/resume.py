from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# 基础信息模型
class SkillInfo(BaseModel):
    """技能信息模型"""
    name: str = Field(..., description="技能名称")
    level: Optional[str] = Field(None, description="技能水平")
    description: Optional[str] = Field(None, description="技能描述")


class CertificateInfo(BaseModel):
    """证书信息模型"""
    name: str = Field(..., description="证书名称")
    issuer: Optional[str] = Field(None, description="发证机构")
    issue_date: Optional[str] = Field(None, description="发证日期")
    expire_date: Optional[str] = Field(None, description="到期日期")


class WorkHistoryInfo(BaseModel):
    """工作经历信息模型"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    description: Optional[str] = Field(None, description="工作描述")


class EducationExperience(BaseModel):
    """教育经历信息模型"""
    school: str = Field(..., description="学校名称")
    major: Optional[str] = Field(None, description="专业")
    degree: Optional[str] = Field(None, description="学位")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    description: Optional[str] = Field(None, description="在校经历描述")


class Award(BaseModel):
    """获奖经历信息模型"""
    name: str = Field(..., description="奖项名称")
    level: Optional[str] = Field(None, description="奖项级别")
    issuer: Optional[str] = Field(None, description="颁发机构")
    award_date: Optional[str] = Field(None, description="获奖日期")
    description: Optional[str] = Field(None, description="奖项描述")


# 简历相关模型
class ResumeBase(BaseModel):
    """简历基础模型"""
    
    # 文件信息
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    resume_type: Optional[str] = "general"
    content: Optional[str] = Field(None, description="简历内容")
    parsed_data: Optional[Dict[str, Any]] = None
    
    # 处理状态
    processing_status: Optional[str] = None
    processing_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    # 个人基本信息
    name: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None
    id_number: Optional[str] = Field(None, description="身份证号")
    phone: Optional[str] = None
    email: Optional[str] = None
    stature: Optional[str] = Field(None, description="身高")
    weight: Optional[str] = Field(None, description="体重")
    nation: Optional[str] = Field(None, description="民族")
    english_level: Optional[str] = Field(None, description="英语水平")
    
    # 个人状态信息
    political_status: Optional[str] = Field(None, description="政治面貌")
    marital_status: Optional[str] = Field(None, description="婚姻状况")
    hukou: Optional[str] = Field(None, description="户口所在地")
    current_address: Optional[str] = Field(None, description="当前住址")
    city: Optional[str] = Field(None, description="所在城市")
    district: Optional[str] = Field(None, description="所在区域")
    
    # 教育信息
    highest_education: Optional[str] = None
    highest_degree: Optional[str] = None
    major: Optional[str] = None
    graduate_school: Optional[str] = None
    graduation_date: Optional[datetime] = None
    
    # 工作信息
    experience_years: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    current_salary: Optional[str] = Field(None, description="当前薪资")
    work_time: Optional[str] = Field(None, description="参加工作时间")
    
    # 职称信息
    talent_name: Optional[str] = Field(None, description="职称名称")
    talent_team: Optional[str] = Field(None, description="职称等级")
    talent_type: Optional[str] = Field(None, description="人才类别")
    title_rank: Optional[str] = Field(None, description="技能等级")
    
    # 经历信息
    work_history: Optional[List[WorkHistoryInfo]] = Field(
        None, 
        description="工作经历"
    )
    edu_experience: Optional[List[EducationExperience]] = Field(
        None, 
        description="教育经历"
    )
    awards: Optional[List[Award]] = Field(None, description="获奖经历")
    
    # 求职意向
    expected_position: Optional[str] = None
    expected_salary: Optional[str] = None
    expected_location: Optional[str] = None
    
    # 技能与证书
    skills: Optional[List[SkillInfo]] = Field(
        None, 
        description="技能列表"
    )
    certificates: Optional[List[CertificateInfo]] = Field(
        None, 
        description="证书列表"
    )
    
    # 其他信息
    family_situation: Optional[str] = Field(None, description="家庭情况")
    
    # 匹配状态
    matching_status: Optional[str] = None
    matching_score: Optional[int] = None
    
    # 版本信息
    resume_version: Optional[int] = Field(1, description="简历版本")
    is_latest: Optional[bool] = Field(True, description="是否最新版本")
    
    # 来源信息
    source_channel: Optional[str] = Field(None, description="来源渠道")
    source_batch: Optional[str] = Field(None, description="来源批次")
    
    # 质量评分
    completeness_score: Optional[int] = None
    
    # 关联关系
    repository_id: Optional[int] = None
    candidate_id: Optional[int] = Field(None, description="候选人ID")
    talent_id: Optional[int] = Field(None, description="人才ID")
    tenant_id: Optional[int] = None
    
    # 发布者信息
    publisher_id: Optional[int] = None
    publisher_type: Optional[str] = None
    publisher_name: Optional[str] = None
    
    # 审核信息
    review_status: Optional[str] = "pending"
    review_comment: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "R1234567899",
                "repository_id": 1,
                "name": "张三",
                "gender": "男",
                "birthdate": "1990-01-01T00:00:00",
                "id_number": "110101199001010011",
                "phone": "13800138000",
                "email": "zhangsan@example.com",
                "stature": "178cm",
                "weight": "70kg",
                "nation": "汉族",
                "english_level": "CET-6",
                "political_status": "群众",
                "marital_status": "未婚",
                "hukou": "北京市海淀区",
                "current_address": "北京市朝阳区建国路88号",
                "city": "北京",
                "district": "朝阳区",
                "highest_education": "本科",
                "highest_degree": "学士",
                "major": "计算机科学",
                "graduate_school": "北京大学",
                "graduation_date": "2018-07-01T00:00:00",
                "experience_years": 5,
                "current_company": "ABC科技有限公司",
                "current_position": "高级工程师",
                "current_salary": "25000",
                "work_time": "2018-07",
                "talent_name": "软件工程师",
                "talent_team": "中级",
                "talent_type": "技术人才",
                "title_rank": "中级职称",
                "work_history": [
                    {
                        "company": "ABC科技有限公司",
                        "position": "高级工程师",
                        "start_date": "2018-01",
                        "end_date": "2022-12",
                        "description": "负责核心系统开发"
                    },
                    {
                        "company": "XYZ信息技术有限公司",
                        "position": "软件工程师",
                        "start_date": "2015-07",
                        "end_date": "2017-12",
                        "description": "参与Web应用开发"
                    }
                ],
                "edu_experience": [
                    {
                        "school": "北京大学",
                        "major": "计算机科学",
                        "degree": "学士",
                        "start_date": "2014-09",
                        "end_date": "2018-07",
                        "description": "主修人工智能和数据库系统"
                    }
                ],
                "awards": [
                    {
                        "name": "优秀员工",
                        "level": "公司级",
                        "issuer": "ABC科技有限公司",
                        "award_date": "2021-12",
                        "description": "年度技术创新奖"
                    }
                ],
                "expected_position": "技术经理",
                "expected_salary": "30000-35000",
                "expected_location": "北京",
                "skills": [
                    {
                        "name": "Python",
                        "level": "精通",
                        "description": "5年项目经验"
                    },
                    {
                        "name": "数据库设计",
                        "level": "熟练",
                        "description": "熟悉MySQL、PostgreSQL"
                    },
                    {
                        "name": "机器学习",
                        "level": "良好",
                        "description": "有实际项目经验"
                    }
                ],
                "certificates": [
                    {
                        "name": "PMP项目管理认证",
                        "issuer": "PMI",
                        "issue_date": "2020-05",
                        "expire_date": "2023-05"
                    }
                ],
                "family_situation": "父母健在，有一个姐姐",
                "source_channel": "官网投递",
                "source_batch": "2023春季招聘",
            }
        }
    }


class ResumeCreate(ResumeBase):
    """简历创建模型"""
    resume_id: Optional[str] = Field(None, description="简历ID，不提供则自动生成")
    repository_id: Optional[int] = Field(None, description="简历库ID，可选")
    tenant_id: Optional[int] = Field(None, description="租户ID")
    
    # 以下字段可选，支持无文件创建简历
    file_name: Optional[str] = Field(None, description="文件名")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_type: Optional[str] = Field(None, description="文件类型")
    is_manual_entry: Optional[bool] = Field(False, description="是否为手动创建的简历")
    
    # 工作经历、教育经历、技能等复杂结构
    work_history: Optional[List[WorkHistoryInfo]] = Field(
        None, 
        description="工作经历"
    )
    edu_experience: Optional[List[EducationExperience]] = Field(
        None, 
        description="教育经历"
    )
    awards: Optional[List[Award]] = Field(
        None, 
        description="获奖经历"
    )
    skills: Optional[List[SkillInfo]] = Field(
        None, 
        description="技能列表"
    )
    certificates: Optional[List[CertificateInfo]] = Field(
        None, 
        description="证书列表"
    )
    
    # 发布者信息由系统自动填充
    publisher_id: Optional[int] = Field(None, description="发布者ID")
    publisher_type: Optional[str] = Field(None, description="发布者类型")
    publisher_name: Optional[str] = Field(None, description="发布者姓名")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "R1234567899",
                "repository_id": 1,
                "name": "张三",
                "gender": "男",
                "birthdate": "1990-01-01T00:00:00",
                "id_number": "110101199001010011",
                "phone": "13800138000",
                "email": "zhangsan@example.com",
                "stature": "178cm",
                "weight": "70kg",
                "nation": "汉族",
                "english_level": "CET-6",
                "political_status": "群众",
                "marital_status": "未婚",
                "hukou": "北京市海淀区",
                "current_address": "北京市朝阳区建国路88号",
                "city": "北京",
                "district": "朝阳区",
                "highest_education": "本科",
                "highest_degree": "学士",
                "major": "计算机科学",
                "graduate_school": "北京大学",
                "graduation_date": "2018-07-01T00:00:00",
                "experience_years": 5,
                "current_company": "ABC科技有限公司",
                "current_position": "高级工程师",
                "current_salary": "25000",
                "work_time": "2018-07",
                "talent_name": "软件工程师",
                "talent_team": "中级",
                "talent_type": "技术人才",
                "title_rank": "中级职称",
                "work_history": [
                    {
                        "company": "ABC科技有限公司",
                        "position": "高级工程师",
                        "start_date": "2018-01",
                        "end_date": "2022-12",
                        "description": "负责核心系统开发"
                    },
                    {
                        "company": "XYZ信息技术有限公司",
                        "position": "软件工程师",
                        "start_date": "2015-07",
                        "end_date": "2017-12",
                        "description": "参与Web应用开发"
                    }
                ],
                "edu_experience": [
                    {
                        "school": "北京大学",
                        "major": "计算机科学",
                        "degree": "学士",
                        "start_date": "2014-09",
                        "end_date": "2018-07",
                        "description": "主修人工智能和数据库系统"
                    }
                ],
                "awards": [
                    {
                        "name": "优秀员工",
                        "level": "公司级",
                        "issuer": "ABC科技有限公司",
                        "award_date": "2021-12",
                        "description": "年度技术创新奖"
                    }
                ],
                "expected_position": "技术经理",
                "expected_salary": "30000-35000",
                "expected_location": "北京",
                "skills": [
                    {
                        "name": "Python",
                        "level": "精通",
                        "description": "5年项目经验"
                    },
                    {
                        "name": "数据库设计",
                        "level": "熟练",
                        "description": "熟悉MySQL、PostgreSQL"
                    },
                    {
                        "name": "机器学习",
                        "level": "良好",
                        "description": "有实际项目经验"
                    }
                ],
                "certificates": [
                    {
                        "name": "PMP项目管理认证",
                        "issuer": "PMI",
                        "issue_date": "2020-05",
                        "expire_date": "2023-05"
                    }
                ],
                "family_situation": "父母健在，有一个姐姐",
                "source_channel": "官网投递",
                "source_batch": "2023春季招聘",
            }
        }
    }


class ResumeUpdate(ResumeBase):
    """简历更新模型"""
    skills: Optional[List[SkillInfo]] = Field(
        None, 
        description="技能列表"
    )
    certificates: Optional[List[CertificateInfo]] = Field(
        None, 
        description="证书列表"
    )
    processing_status: Optional[str] = None
    processing_message: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    matching_status: Optional[str] = None
    matching_score: Optional[int] = None
    completeness_score: Optional[int] = None
    
    # 审核信息更新
    review_status: Optional[str] = None
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None


class ResumeInDBBase(ResumeBase):
    id: int
    resume_id: str
    file_path: Optional[str] = None
    repository_id: Optional[int] = None
    tenant_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    processing_status: str
    
    # 发布信息
    publisher_id: Optional[int] = None
    publisher_type: Optional[str] = None
    publisher_name: Optional[str] = None
    publish_time: Optional[datetime] = None
    
    # 审核信息
    review_status: str
    reviewer_id: Optional[int] = None
    review_time: Optional[datetime] = None
    review_comment: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class Resume(ResumeInDBBase):
    """简历完整模型"""
    id: int = Field(..., description="主键ID")
    resume_id: str = Field(..., description="简历ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ResumeBasicInfo(BaseModel):
    """简历基本信息模型"""
    id: int = Field(..., description="主键ID")
    resume_id: str = Field(..., description="简历ID")
    file_name: Optional[str] = Field(None, description="文件名")
    resume_type: str = Field(..., description="简历类型")
    processing_status: str = Field(..., description="处理状态")
    name: Optional[str] = Field(None, description="姓名")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = {
        "from_attributes": True
    }


class ResumeList(BaseModel):
    """简历列表响应模型"""
    items: List[Resume]
    total: int
    page: int
    limit: int
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "resume_id": "R1234567890",
                        "name": "张三",
                        "phone": "13800138000",
                        "email": "zhangsan@example.com",
                        "created_at": "2023-01-01T12:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 10
            }
        }
    }


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    VALIDATION_FAILED = "validation_failed"
    FAILED = "failed" 
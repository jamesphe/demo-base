from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from .common import ListResponse


class TrialApplicationBase(BaseModel):
    """试用申请基础模型"""
    status: str = Field("pending", description="申请状态")
    

class TrialApplicationCreate(BaseModel):
    """试用申请创建模型"""
    company_name: str = Field(..., description="公司名称")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    contact_email: EmailStr = Field(..., description="联系邮箱")
    company_size: Optional[str] = Field(None, description="公司规模")
    business_description: Optional[str] = Field(None, description="业务描述")
    application_reason: Optional[str] = Field(None, description="申请原因")
    user_id: Optional[int] = Field(None, description="用户ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "示例科技有限公司",
                "contact_name": "张三",
                "contact_phone": "13800138000",
                "contact_email": "zhangsan@example.com",
                "company_size": "100-499人",
                "business_description": "专注于人工智能解决方案",
                "application_reason": "希望使用产品提升效率"
            }
        }
    }


class TrialApplicationUpdate(BaseModel):
    """试用申请更新模型"""
    status: Optional[str] = Field(None, description="申请状态")
    trial_start_date: Optional[datetime] = Field(None, description="试用开始日期")
    trial_end_date: Optional[datetime] = Field(None, description="试用结束日期")
    reject_reason: Optional[str] = Field(None, description="拒绝原因")
    company_name: Optional[str] = Field(None, description="公司名称")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[EmailStr] = Field(None, description="联系邮箱")
    company_size: Optional[str] = Field(None, description="公司规模")
    business_description: Optional[str] = Field(None, description="业务描述")
    application_reason: Optional[str] = Field(None, description="申请原因")
    user_id: Optional[int] = Field(None, description="用户ID")


class TrialApplicationInDBBase(BaseModel):
    """数据库中的试用申请模型"""
    id: int = Field(..., description="主键ID")
    status: str = Field(..., description="申请状态")
    user_id: Optional[int] = Field(None, description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    trial_start_date: Optional[datetime] = Field(None, description="试用开始日期")
    trial_end_date: Optional[datetime] = Field(None, description="试用结束日期")
    reject_reason: Optional[str] = Field(None, description="拒绝原因")
    company_name: str = Field(..., description="公司名称")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    contact_email: EmailStr = Field(..., description="联系邮箱")
    company_size: Optional[str] = Field(None, description="公司规模")
    business_description: Optional[str] = Field(None, description="业务描述")
    application_reason: Optional[str] = Field(None, description="申请原因")

    model_config = {
        "from_attributes": True
    }


class TrialApplication(TrialApplicationInDBBase):
    """完整的试用申请模型"""
    pass


class TrialStatus(BaseModel):
    """试用状态模型"""
    status: str = Field(..., description="试用状态")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    trial_start_date: Optional[datetime] = Field(None, description="试用开始日期")
    trial_end_date: Optional[datetime] = Field(None, description="试用结束日期")
    reject_reason: Optional[str] = Field(None, description="拒绝原因")
    company_name: Optional[str] = Field(None, description="公司名称")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    user_id: Optional[int] = Field(None, description="用户ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "approved",
                "created_at": "2024-01-01T00:00:00",
                "trial_start_date": "2024-01-15T00:00:00",
                "trial_end_date": "2024-02-15T00:00:00",
                "company_name": "示例科技有限公司",
                "contact_name": "张三"
            }
        }
    }


# 添加列表响应模型
class TrialApplicationListResponse(ListResponse[TrialApplication]):
    """试用申请列表响应模型"""
    pass 
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .common import ListResponse


# 共享属性
class CertificationBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    issuing_organization: Optional[str] = None
    status: Optional[str] = "active"


# 创建时使用
class CertificationCreate(CertificationBase):
    tenant_id: Optional[int] = None


# 更新时使用
class CertificationUpdate(CertificationBase):
    name: Optional[str] = None
    tenant_id: Optional[int] = None


# 数据库中返回的完整模型
class CertificationInDBBase(CertificationBase):
    id: int
    tenant_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API中返回的模型
class Certification(CertificationInDBBase):
    pass


# 返回多个证书的模型
class CertificationList(BaseModel):
    total: int
    items: List[Certification]


class CertificationListResponse(ListResponse[Certification]):
    """证书列表响应模型"""
    pass
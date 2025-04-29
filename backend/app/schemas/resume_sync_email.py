from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .common import Meta


class ResumeSyncEmailBase(BaseModel):
    """简历同步邮箱基础模型"""
    email: str
    imap_server: str
    imap_port: int = 993
    smtp_server: str
    smtp_port: int = 465
    is_active: bool = True
    sync_interval: int = 15
    description: Optional[str] = None


class ResumeSyncEmailCreate(ResumeSyncEmailBase):
    """创建简历同步邮箱请求模型"""
    password: str


class ResumeSyncEmailUpdate(BaseModel):
    """更新简历同步邮箱请求模型"""
    email: Optional[str] = None
    password: Optional[str] = None
    imap_server: Optional[str] = None
    imap_port: Optional[int] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    is_active: Optional[bool] = None
    sync_interval: Optional[int] = None
    description: Optional[str] = None


class ResumeSyncEmail(ResumeSyncEmailBase):
    """简历同步邮箱完整模型"""
    id: int
    tenant_id: int
    last_sync_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeSyncEmailListResponse(BaseModel):
    """简历同步邮箱列表响应模型"""
    data: List[ResumeSyncEmail]
    meta: Meta


class JobKeywordBase(BaseModel):
    """职位关键字基础模型"""
    keyword: str
    description: Optional[str] = None


class JobKeywordCreate(JobKeywordBase):
    """创建职位关键字请求模型"""
    job_id: int
    sync_email_id: int


class JobKeywordUpdate(BaseModel):
    """更新职位关键字请求模型"""
    keyword: Optional[str] = None
    description: Optional[str] = None


class JobKeyword(JobKeywordBase):
    """职位关键字完整模型"""
    id: int
    job_id: int
    sync_email_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
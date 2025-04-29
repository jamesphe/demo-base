from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class ResumeSyncEmailBase(BaseModel):
    email: EmailStr
    password: str
    imap_server: str
    imap_port: Optional[int] = 993
    smtp_server: str
    smtp_port: Optional[int] = 465
    is_active: Optional[bool] = True
    sync_interval: Optional[int] = 15
    description: Optional[str] = None

class ResumeSyncEmailCreate(ResumeSyncEmailBase):
    tenant_id: int

class ResumeSyncEmailUpdate(ResumeSyncEmailBase):
    pass

class ResumeSyncEmail(ResumeSyncEmailBase):
    id: int
    tenant_id: int
    last_sync_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class JobKeywordBase(BaseModel):
    job_id: int
    keyword: constr(min_length=1, max_length=255)
    description: Optional[str] = None

class JobKeywordCreate(JobKeywordBase):
    sync_email_id: int

class JobKeywordUpdate(JobKeywordBase):
    pass

class JobKeyword(JobKeywordBase):
    id: int
    sync_email_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 
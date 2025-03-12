from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    content: str
    type: str  # 通知类型：system, resume, interview 等
    user_id: int  # 接收用户ID
    is_read: Optional[bool] = False
    tenant_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(NotificationBase):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
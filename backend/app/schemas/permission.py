from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .common import ListResponse


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionInDBBase(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class Permission(PermissionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PermissionListResponse(ListResponse[Permission]):
    """权限列表响应模型"""
    pass 
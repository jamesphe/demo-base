from typing import Optional
from pydantic import BaseModel
from datetime import datetime


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


class Permission(PermissionInDBBase):
    pass 
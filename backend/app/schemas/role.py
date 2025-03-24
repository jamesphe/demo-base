from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .permission import Permission


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None


class Role(RoleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class RoleWithPermissions(RoleBase):
    permissions: List[Permission] = [] 
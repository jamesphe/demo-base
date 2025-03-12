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


class RoleInDBBase(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class Role(RoleInDBBase):
    pass


class RoleWithPermissions(RoleInDBBase):
    permissions: List[Permission] = [] 
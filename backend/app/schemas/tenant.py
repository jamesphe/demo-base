from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class TenantBase(BaseModel):
    tenant_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    external_id: Optional[str] = None
    status: str = "active"


class TenantCreate(TenantBase):
    pass


class TenantUpdate(TenantBase):
    tenant_name: Optional[str] = None
    status: Optional[str] = None


class TenantInDBBase(TenantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class Tenant(TenantInDBBase):
    pass 
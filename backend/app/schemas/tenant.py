from typing import Optional, List
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

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None
        }


class Tenant(TenantInDBBase):
    pass


class TenantListResponse(BaseModel):
    data: List[Tenant]
    meta: dict 
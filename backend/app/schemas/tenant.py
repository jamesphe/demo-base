from typing import List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class TenantBase(BaseModel):
    tenant_name: str = Field(..., alias="tenantName")
    contact_person: str = Field(None, alias="contactPerson")
    phone: str = Field(None)
    email: EmailStr = Field(None)
    address: str = Field(None)
    external_id: str | None = Field(None, alias="externalId")
    status: str = Field("active")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }


class TenantCreate(TenantBase):
    pass


class TenantUpdate(TenantBase):
    pass


class TenantInDBBase(TenantBase):
    id: int
    created_at: datetime = Field(None, alias="createdAt")
    updated_at: datetime = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True


class Tenant(TenantInDBBase):
    pass


class TenantListResponse(BaseModel):
    data: List[Tenant]
    meta: dict 
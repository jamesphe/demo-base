from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserType(str, Enum):
    candidate = 'candidate'
    tenant = 'tenant'
    admin = 'admin'

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    user_type: Optional[UserType] = UserType.tenant
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    tenant_id: Optional[int] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str
    user_type: Optional[str] = None
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    external_tenant_id: Optional[str] = None
    tenant_id: Optional[int] = None

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserInfo(BaseModel):
    id: int
    email: EmailStr
    username: str
    name: str
    user_type: UserType
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    roles: List[str]
    is_active: bool
    is_superuser: bool
    tenant_id: Optional[int] = None
    phone: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }

class UserInfoResponse(BaseModel):
    code: int = 20000
    data: UserInfo 

class UserRoleUpdate(BaseModel):
    user_id: int
    role_ids: List[int] 

class TenantInfo(BaseModel):
    id: int
    name: str
    code: str

class RoleInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class UserWithTenantAndRoles(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: Optional[str] = None
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    tenant_id: Optional[int] = None
    tenant_name: Optional[str] = None
    role_names: List[str] = []
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    roles: List[RoleInfo] = []
    tenant: Optional[TenantInfo] = None

    class Config:
        from_attributes = True

class Meta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int

class UserListResponse(BaseModel):
    data: List[UserWithTenantAndRoles]
    meta: Meta 
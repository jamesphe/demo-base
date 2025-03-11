from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    username: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    username: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserInfo(BaseModel):
    name: str
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    roles: List[str]
    
    model_config = {
        "from_attributes": True
    }

class UserInfoResponse(BaseModel):
    code: int = 20000
    data: UserInfo 
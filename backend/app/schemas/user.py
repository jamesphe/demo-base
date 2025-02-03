from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import validator

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    username: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str

    @validator('email')
    def email_as_username(cls, v):
        return v

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str 
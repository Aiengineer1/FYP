from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    mall_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    mall_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class MallStatusResponse(BaseModel):
    has_mall: bool
    mall_id: Optional[int]

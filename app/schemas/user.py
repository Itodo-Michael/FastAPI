from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar: Optional[str] = None

class UserCreate(UserBase):
    is_verified: bool = False

class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = None

class User(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

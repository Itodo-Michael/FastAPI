from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    is_verified: bool
    is_admin: bool
    created_at: str  # Это должно быть строкой
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

    # Добавьте валидатор для преобразования datetime в строку
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
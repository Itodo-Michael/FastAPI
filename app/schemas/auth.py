from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.user import User

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    email: str
    is_admin: bool = False
    is_verified: bool = False

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    avatar: Optional[str] = None

    @field_validator('name', 'email', 'password')
    @classmethod
    def validate_not_empty(cls, v, info):
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} cannot be empty')
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @')
        return v.lower()

class RefreshRequest(BaseModel):
    refresh_token: str

class SessionInfo(BaseModel):
    id: int
    user_agent: Optional[str]
    created_at: str
    expires_at: str

   
    
    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    user: User
    tokens: Token

class LoginResponse(BaseModel):
    user: User
    tokens: Token 
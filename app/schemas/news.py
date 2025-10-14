from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional
from .user import User

class NewsBase(BaseModel):
    title: str
    content: dict[str, Any]  # CHANGE BACK to dict for JSON
    cover: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict[str, Any]] = None  # CHANGE BACK to dict
    cover: Optional[str] = None

class News(NewsBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    
    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import User

class CommentBase(BaseModel):
    text: str  # Must be 'text' to match database column name

class CommentCreate(CommentBase):
    news_id: int  # Keep news_id field

class CommentUpdate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    news_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    
    class Config:
        from_attributes = True
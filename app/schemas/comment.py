from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import User

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

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

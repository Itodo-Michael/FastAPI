from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar = Column(Text, nullable=True)
    
    # Lazy relationships
    news = relationship("News", back_populates="author", cascade="all, delete-orphan", lazy="select")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan", lazy="select")

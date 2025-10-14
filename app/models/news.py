from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class News(BaseModel):
    __tablename__ = "news"
    
    title = Column(String(200), nullable=False)
    content = Column(JSON, nullable=False)
    cover = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="news")
    comments = relationship("Comment", back_populates="news", cascade="all, delete-orphan")
from sqlalchemy import Column, Text, ForeignKey, Integer  # Added Integer
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class Comment(BaseModel):
    __tablename__ = "comments"
    
    text = Column(Text, nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    news = relationship("News", back_populates="comments")
    author = relationship("User", back_populates="comments")

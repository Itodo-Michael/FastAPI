from sqlalchemy import Column, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class Comment(BaseModel):
    __tablename__ = "comments"
    
    text = Column(Text, nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Lazy relationships
    news = relationship("News", back_populates="comments", lazy="select")
    author = relationship("User", back_populates="comments", lazy="select")

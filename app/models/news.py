from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import BaseModel

class News(BaseModel):
    __tablename__ = "news"
    
    title = Column(String(200), nullable=False)
    content = Column(JSON, nullable=False)
    cover = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Lazy relationships
    author = relationship("User", back_populates="news", lazy="select")
    comments = relationship("Comment", back_populates="news", cascade="all, delete-orphan", lazy="select")

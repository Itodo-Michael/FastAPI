from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class RefreshSession(BaseModel):
    __tablename__ = "refresh_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=False)
    user_agent = Column(String(512), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Use string-based relationship to avoid circular imports
    user = relationship("User", back_populates="sessions")
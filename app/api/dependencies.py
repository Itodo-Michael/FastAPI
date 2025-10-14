from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.crud import user as user_crud

def get_verified_user(author_id: int, db: Session = Depends(get_db)):
    user = user_crud.user.get(db, author_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User is not verified to perform this action")
    return user

from .dependencie.auth import (
    get_current_user,
    get_current_verified_user, 
    get_current_admin_user,
    news_owner_or_admin,
    comment_owner_or_admin
)

__all__ = [
    "get_current_user",
    "get_current_verified_user",
    "get_current_admin_user", 
    "news_owner_or_admin",
    "comment_owner_or_admin"
]
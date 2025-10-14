from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.crud import user as user_crud
from app.crud import news as news_crud
from app.crud import comment as comment_crud
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = AuthService.verify_token(credentials.credentials)
    user = user_crud.user.get(db, id=token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

async def get_current_verified_user(current_user: dict = Depends(get_current_user)):
    if not current_user.is_verified and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified"
        )
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def news_owner_or_admin(
    news_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency to check if current user is the news owner OR admin
    """
    news = news_crud.news.get(db, id=news_id)
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Allow if user is the owner OR user is admin
    if news.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to modify this news"
        )
    
    return news  # Return the news item, not the user

def comment_owner_or_admin(
    comment_id: int,
    db: Session = Depends(get_db),  # ADDED Depends here
    current_user = Depends(get_current_user)  # ADDED Depends here
):
    """
    Dependency to check if current user is the comment owner OR admin
    """
    comment = comment_crud.comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this comment"
        )
    return comment  # Return the comment item
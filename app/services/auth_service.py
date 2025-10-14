from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
import secrets

from app.core.config import settings
from app.models.user import User
from app.models.session import RefreshSession
from app.schemas.auth import TokenData

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(user: User, expires_delta: Optional[timedelta] = None):
        print(f"🎯 Creating token for user: {user.email}, is_admin: {user.is_admin}")
        
        # FIXED: Convert user.id to string for JWT compliance
        to_encode = {
            "sub": str(user.id),  # ← THIS IS THE FIX
            "email": user.email,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified
        }

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        print(f"🎯 Token created with payload: {to_encode}")
        return encoded_jwt

    @staticmethod
    def create_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    @staticmethod
    def verify_token(token: str) -> TokenData:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Handle both string and integer subject
            user_id = payload.get("sub")
            if user_id is None:
                raise credentials_exception
                
            # Convert to integer if it's a string, or keep as is if it's already an integer
            if isinstance(user_id, str):
                user_id = int(user_id)
            
            email: str = payload.get("email")
            is_admin: bool = payload.get("is_admin", False)
            is_verified: bool = payload.get("is_verified", False)
            
            if email is None:
                raise credentials_exception
            
            print(f"Token verified - User ID: {user_id}, Email: {email}, Admin: {is_admin}")
            return TokenData(user_id=user_id, email=email, is_admin=is_admin, is_verified=is_verified)
        except (JWTError, ValueError) as e:
            print(f"Token verification failed: {e}")
            raise credentials_exception

    @staticmethod
    def create_refresh_session(db: Session, user_id: int, user_agent: Optional[str] = None) -> RefreshSession:
        refresh_token = AuthService.create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        session = RefreshSession(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_refresh_session(db: Session, refresh_token: str) -> Optional[RefreshSession]:
        return db.query(RefreshSession).filter(
            RefreshSession.refresh_token == refresh_token,
            RefreshSession.expires_at > datetime.utcnow()
        ).first()

    @staticmethod
    def delete_refresh_session(db: Session, refresh_token: str) -> None:
        session = db.query(RefreshSession).filter(RefreshSession.refresh_token == refresh_token).first()
        if session:
            db.delete(session)
            db.commit()

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> list[RefreshSession]:
        return db.query(RefreshSession).filter(
            RefreshSession.user_id == user_id,
            RefreshSession.expires_at > datetime.utcnow()
        ).all()
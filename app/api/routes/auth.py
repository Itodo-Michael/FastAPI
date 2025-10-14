from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError, jwt  # Add this import
from fastapi.security import OAuth2PasswordBearer  # Add th
from app.database.session import get_db
from app.schemas.auth import Token, LoginRequest, RegisterRequest, RefreshRequest, SessionInfo, RegisterResponse, LoginResponse
from app.schemas.user import User
from app.services.auth_service import AuthService
from app.crud import user as user_crud
from app.core.config import settings  # Add this import
from app.api.dependencie.auth import get_current_user, get_current_admin_user 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(user_data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    print(f"=== REGISTRATION START ===")
    print(f"Received data: {user_data}")
    
    try:
        # Check if user already exists
        existing_user = user_crud.user.get_by_email(db, email=user_data.email)
        if existing_user:
            print(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "hashed_password": AuthService.get_password_hash(user_data.password),
            "avatar": user_data.avatar,
            "is_verified": False,
            "is_admin": False
        }
        print(f"Creating user with: {user_dict}")
        
        user = user_crud.user.create(db, obj_in=user_dict)
        print(f"User created successfully: {user.id}")
        
        # FIXED: Use user object instead of data dict
        access_token = AuthService.create_access_token(user=user)
        refresh_session = AuthService.create_refresh_session(
            db, user.id, request.headers.get("user-agent")
        )
        
        return RegisterResponse(
            user=user,
            tokens=Token(
                access_token=access_token,
                refresh_token=refresh_session.refresh_token,
                token_type="bearer"
            )
        )
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    print(f"=== LOGIN ATTEMPT ===")
    print(f"Login data: {login_data.email}")
    
    user = user_crud.user.get_by_email(db, email=login_data.email)
    if not user:
        print(f"User not found: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not AuthService.verify_password(login_data.password, user.hashed_password):
        print(f"Invalid password for user: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    print(f"Login successful for user: {user.id}")
    
    # FIXED: Use user object instead of data dict
    access_token = AuthService.create_access_token(user=user)
    refresh_session = AuthService.create_refresh_session(
        db, user.id, request.headers.get("user-agent")
    )
    
    return LoginResponse(
        user=user,
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_session.refresh_token,
            token_type="bearer"
        )
    )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    session = AuthService.get_refresh_session(db, refresh_data.refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # FIXED: Use user object instead of data dict
    access_token = AuthService.create_access_token(user=session.user)
    
    # Delete old session and create new one
    AuthService.delete_refresh_session(db, refresh_data.refresh_token)
    new_refresh_session = AuthService.create_refresh_session(
        db, session.user_id, request.headers.get("user-agent")
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_session.refresh_token,
        token_type="bearer"
    )

@router.post("/logout")
def logout(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    AuthService.delete_refresh_session(db, refresh_data.refresh_token)
    return {"message": "Successfully logged out"}

@router.get("/sessions", response_model=list[SessionInfo])
def get_my_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = AuthService.get_user_sessions(db, current_user.id)
    return sessions

@router.get("/check")
async def check_auth(current_user: User = Depends(get_current_user)):
    """Check if user is authenticated and return user data"""
    return current_user

@router.get("/check-admin/{user_id}")
def check_admin_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = user_crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified
    }


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.database.session import get_db
from app.schemas.auth import Token
from app.services.auth_service import AuthService
from app.crud import user as user_crud
from app.core.config import settings
import secrets

router = APIRouter()

@router.get("/github/demo")
async def github_demo():
    """Demo GitHub OAuth - redirects to a mock authentication"""
    # For demo purposes, create a mock GitHub-like flow
    state = secrets.token_urlsafe(16)
    return RedirectResponse(f"/auth/oauth/github/callback?code=demo_{state}&state={state}")

@router.get("/github/login")
async def github_login():
    """Redirect to GitHub OAuth"""
    # Since we don't have real GitHub app, redirect to demo
    return RedirectResponse("/auth/oauth/github/demo")

@router.get("/github/callback", response_model=Token)
async def github_callback(
    request: Request, 
    code: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        # Mock GitHub user data for demo
        if code and code.startswith("demo_"):
            # Create mock user data for demo
            mock_user_data = {
                "id": "github_12345",
                "email": f"github_user_{secrets.token_hex(8)}@example.com",
                "display_name": f"GitHub User {secrets.token_hex(4)}",
                "picture": "https://avatars.githubusercontent.com/u/583231?v=4"
            }
        else:
            # In real implementation, you would verify with GitHub API
            raise HTTPException(status_code=400, detail="Invalid OAuth code")
        
        # Check if user exists by GitHub ID
        user = user_crud.user.get_by_github_id(db, github_id=mock_user_data["id"])
        
        if not user:
            # Check if user exists by email
            if mock_user_data["email"]:
                user = user_crud.user.get_by_email(db, email=mock_user_data["email"])
            
            if not user:
                # Create new user
                user_data = {
                    "name": mock_user_data["display_name"],
                    "email": mock_user_data["email"],
                    "github_id": mock_user_data["id"],
                    "avatar": mock_user_data["picture"],
                    "is_verified": True,  # Auto-verify GitHub users for demo
                    "is_admin": False
                }
                user = user_crud.user.create(db, obj_in=user_data)
            else:
                # Update existing user with GitHub ID
                user.github_id = mock_user_data["id"]
                if not user.avatar:
                    user.avatar = mock_user_data["picture"]
                db.commit()
                db.refresh(user)
        
        # Create tokens
        access_token = AuthService().create_access_token(data={"sub": user.id})
        refresh_session = AuthService.create_refresh_session(
            db, user.id, request.headers.get("user-agent")
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_session.refresh_token,
            token_type="bearer"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
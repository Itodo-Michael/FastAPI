from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.crud import user as user_crud
from app.api.dependencies import get_current_admin_user

router = APIRouter()

@router.post("/users/{user_id}/make-admin")
def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    user = user_crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = True
    user.is_verified = True
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.email} is now an admin"}
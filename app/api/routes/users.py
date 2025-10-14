from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import user as user_crud
from app.api.dependencie.auth import get_current_user, get_current_admin_user  

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.user.create(db, obj_in=user)

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_crud.user.get_all(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.user.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin or the user themselves can update
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    db_user = user_crud.user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being changed and if it already exists
    if user.email and user.email != db_user.email:
        existing_user = user_crud.user.get_by_email(db, email=user.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400, 
                detail="Email already registered to another user"
            )
    
    return user_crud.user.update(db, id=user_id, obj_in=user)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete user - Admin only (with safety checks)"""
    print(f"🗑️ Attempting to delete user {user_id} by admin {current_admin.email}")
    
    # Safety check 1: Prevent self-deletion
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    # Safety check 2: Get the target user first
    target_user = user_crud.user.get(db, id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Safety check 3: Prevent deleting other admins (optional)
    if target_user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete other administrator accounts"
        )
    
    # Safety check 4: Prevent deleting the system admin (ID 1)
    if user_id == 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the system administrator account"
        )
    
    try:
        success = user_crud.user.delete(db, id=user_id)
        if success:
            print(f"✅ User {user_id} deleted by admin {current_admin.id}")
            return {"message": f"User {user_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"❌ Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

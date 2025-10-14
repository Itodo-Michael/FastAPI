from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base import CRUDBase

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_github_id(self, db: Session, github_id: str) -> Optional[User]:
        return db.query(User).filter(User.github_id == github_id).first()

    def create(self, db: Session, obj_in: dict) -> User:
        # Удаляем None значения чтобы избежать ошибок с БД
        obj_in_data = {k: v for k, v in obj_in.items() if v is not None}
        return super().create(db, obj_in_data)

    def update(self, db: Session, *, id: int, obj_in: UserUpdate) -> User:
        db_obj = self.get(db, id=id)
        if db_obj:
            # Convert Pydantic model to dict, exclude unset values
            update_data = obj_in.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> bool:
        user = db.query(User).filter(User.id == id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

user = CRUDUser(User)


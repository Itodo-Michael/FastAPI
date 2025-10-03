from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base import CRUDBase

class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.model_dump()
        return super().create(db, obj_in_data)

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> Optional[User]:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, id, obj_in_data)

user = CRUDUser(User)

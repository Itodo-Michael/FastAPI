from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from .base import CRUDBase

class CRUDComment(CRUDBase[Comment]):
    def get_by_news(self, db: Session, news_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.news_id == news_id).offset(skip).limit(limit).all()

    def get_by_author(self, db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.author_id == author_id).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CommentCreate, author_id: int) -> Comment:  # REMOVED news_id parameter
        obj_in_data = obj_in.model_dump()
        obj_in_data['author_id'] = author_id
        # news_id is already in obj_in from the schema
        return super().create(db, obj_in_data)

    def update(self, db: Session, *, id: int, obj_in: CommentUpdate) -> Comment:
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
    
    def delete(self, db: Session, id: int) -> Comment:
        obj = db.query(Comment).get(id)
        db.delete(obj)
        db.commit()
        return obj

comment = CRUDComment(Comment)
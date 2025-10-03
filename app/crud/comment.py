from sqlalchemy.orm import Session
from typing import List
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from .base import CRUDBase

class CRUDComment(CRUDBase[Comment]):
    def get_by_news(self, db: Session, news_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.news_id == news_id).offset(skip).limit(limit).all()

    def get_by_author(self, db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.author_id == author_id).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CommentCreate, news_id: int, author_id: int) -> Comment:
        obj_in_data = obj_in.model_dump()
        obj_in_data['news_id'] = news_id
        obj_in_data['author_id'] = author_id
        return super().create(db, obj_in_data)

    def update(self, db: Session, id: int, obj_in: CommentUpdate) -> Comment:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, id, obj_in_data)

comment = CRUDComment(Comment)

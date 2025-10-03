from sqlalchemy.orm import Session
from typing import List
from app.models.news import News
from app.schemas.news import NewsCreate, NewsUpdate
from .base import CRUDBase

class CRUDNews(CRUDBase[News]):
    def get_by_author(self, db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[News]:
        return db.query(News).filter(News.author_id == author_id).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: NewsCreate, author_id: int) -> News:
        obj_in_data = obj_in.model_dump()
        obj_in_data['author_id'] = author_id
        return super().create(db, obj_in_data)

    def update(self, db: Session, id: int, obj_in: NewsUpdate) -> News:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        return super().update(db, id, obj_in_data)

news = CRUDNews(News)

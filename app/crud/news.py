from sqlalchemy.orm import Session
from typing import List, Optional
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

    def update(self, db: Session, *, id: int, obj_in: NewsUpdate) -> News:
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
    
    def get_with_author(self, db: Session, id: int) -> Optional[News]:
        return db.query(News).filter(News.id == id).first()
    
    def delete(self, db: Session, id: int) -> News:
        obj = db.query(News).get(id)
        db.delete(obj)
        db.commit()
        return obj

news = CRUDNews(News)
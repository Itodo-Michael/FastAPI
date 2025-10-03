from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.news import News, NewsCreate, NewsUpdate
from app.crud import news as news_crud
from app.api.dependencies import get_verified_user

router = APIRouter()

@router.post("/{author_id}", response_model=News)
def create_news(author_id: int, news: NewsCreate, db: Session = Depends(get_db)):
    # Verify user is authorized to create news
    get_verified_user(author_id, db)
    return news_crud.news.create(db, obj_in=news, author_id=author_id)

@router.get("/", response_model=List[News])
def read_news(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return news_crud.news.get_all(db, skip=skip, limit=limit)

@router.get("/{news_id}", response_model=News)
def read_news_item(news_id: int, db: Session = Depends(get_db)):
    db_news = news_crud.news.get(db, id=news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return db_news

@router.get("/author/{author_id}", response_model=List[News])
def read_news_by_author(author_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return news_crud.news.get_by_author(db, author_id=author_id, skip=skip, limit=limit)

@router.put("/{news_id}", response_model=News)
def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db)):
    db_news = news_crud.news.get(db, id=news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news_crud.news.update(db, id=news_id, obj_in=news)

@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    db_news = news_crud.news.get(db, id=news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    news_crud.news.delete(db, id=news_id)
    return {"message": "News and associated comments deleted successfully"}

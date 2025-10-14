from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.news import News, NewsCreate, NewsUpdate
from app.crud import news as news_crud

# Import the correct dependencies
from app.api.dependencies import get_current_user, get_current_verified_user

router = APIRouter()

@router.post("/{author_id}", response_model=News)
def create_news(
    author_id: int, 
    news: NewsCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_verified_user)
):
    # Security: Users can only create news for themselves, unless admin
    if current_user.id != author_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Can only create news for yourself")
    
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
def update_news(
    news_id: int, 
    news: NewsUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_news = news_crud.news.get(db, id=news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Security: Only author or admin can edit news
    if db_news.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to edit this news")
    
    return news_crud.news.update(db, id=news_id, obj_in=news)

@router.delete("/{news_id}")
def delete_news(
    news_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_news = news_crud.news.get(db, id=news_id)
    if db_news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Security: Only author or admin can delete news
    if db_news.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this news")
    
    news_crud.news.delete(db, id=news_id)
    return {"message": "News and associated comments deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.comment import Comment, CommentCreate, CommentUpdate
from app.crud import comment as comment_crud

router = APIRouter()

@router.post("/{news_id}/{author_id}", response_model=Comment)
def create_comment(news_id: int, author_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return comment_crud.comment.create(db, obj_in=comment, news_id=news_id, author_id=author_id)

@router.get("/", response_model=List[Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return comment_crud.comment.get_all(db, skip=skip, limit=limit)

@router.get("/{comment_id}", response_model=Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.get("/news/{news_id}", response_model=List[Comment])
def read_comments_by_news(news_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return comment_crud.comment.get_by_news(db, news_id=news_id, skip=skip, limit=limit)

@router.put("/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)):
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment_crud.comment.update(db, id=comment_id, obj_in=comment)

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment_crud.comment.delete(db, id=comment_id)
    return {"message": "Comment deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.comment import Comment, CommentCreate, CommentUpdate
from app.crud import comment as comment_crud
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=Comment)
def create_comment(
    comment: CommentCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new comment - ANY authenticated user can comment
    The author_id is automatically set to the current user
    """
    return comment_crud.comment.create(db, obj_in=comment, author_id=current_user.id)

@router.get("/", response_model=List[Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all comments.
    """
    return comment_crud.comment.get_all(db, skip=skip, limit=limit)

# IMPORTANT: This more specific route is placed before the general /{comment_id} route
@router.get("/news/{news_id}", response_model=List[Comment])
def read_comments_by_news(news_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve comments associated with a specific news item.
    """
    return comment_crud.comment.get_by_news(db, news_id=news_id, skip=skip, limit=limit)

@router.get("/{comment_id}", response_model=Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single comment by its ID.
    """
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: int, 
    comment: CommentUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    return comment_crud.comment.update(db, id=comment_id, obj_in=comment)

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a comment. Only the author or an admin can delete.
    """
    db_comment = comment_crud.comment.get(db, id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Manual authorization check
    if db_comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    comment_crud.comment.delete(db, id=comment_id)
    return {"message": "Comment deleted successfully"}
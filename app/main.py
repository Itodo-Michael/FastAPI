from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import json

from app.database.session import engine, get_db
from app.models.base import Base
from app.crud import user as user_crud
from app.crud import news as news_crud
from app.crud import comment as comment_crud
from app.schemas.user import UserCreate
from app.schemas.news import NewsCreate
from app.schemas.comment import CommentCreate

# Initialize FastAPI app
app = FastAPI(
    title="News CRUD API",
    description="CRUD API for news, users, and comments with frontend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")
    templates = None

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>News API - Frontend not configured</h1><p><a href='/docs'>API Docs</a></p>")

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    if templates:
        return templates.TemplateResponse("users.html", {"request": request})
    return HTMLResponse("<h1>Users Management</h1><p>Frontend not configured</p>")

@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    if templates:
        return templates.TemplateResponse("news.html", {"request": request})
    return HTMLResponse("<h1>News Management</h1><p>Frontend not configured</p>")

@app.get("/comments", response_class=HTMLResponse)
async def comments_page(request: Request):
    if templates:
        return templates.TemplateResponse("comments.html", {"request": request})
    return HTMLResponse("<h1>Comments Management</h1><p>Frontend not configured</p>")

# Health Check - FIXED VERSION
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection - FIXED
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "News API", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "service": "News API", "database": "disconnected", "error": str(e)}

# API Routes for Frontend (HTML responses)
@app.get("/api/users", response_class=HTMLResponse)
async def get_users_html(request: Request, db: Session = Depends(get_db)):
    users = user_crud.user.get_all(db)
    if templates:
        return templates.TemplateResponse("components/user_list.html", {
            "request": request,
            "users": users
        })
    return HTMLResponse(f"<p>Users: {len(users)} found</p>")

@app.get("/api/news", response_class=HTMLResponse)
async def get_news_html(request: Request, db: Session = Depends(get_db)):
    news = news_crud.news.get_all(db)
    if templates:
        return templates.TemplateResponse("components/news_list.html", {
            "request": request,
            "news": news
        })
    return HTMLResponse(f"<p>News: {len(news)} found</p>")

@app.get("/api/comments", response_class=HTMLResponse)
async def get_comments_html(request: Request, db: Session = Depends(get_db)):
    comments = comment_crud.comment.get_all(db)
    if templates:
        return templates.TemplateResponse("components/comment_list.html", {
            "request": request,
            "comments": comments
        })
    return HTMLResponse(f"<p>Comments: {len(comments)} found</p>")

# Form Handling Routes (for HTMX)
@app.post("/users", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    is_verified: bool = Form(False),
    avatar: str = Form(None),
    db: Session = Depends(get_db)
):
    user_data = UserCreate(name=name, email=email, is_verified=is_verified, avatar=avatar)
    
    # Check if user already exists
    existing_user = user_crud.user.get_by_email(db, email=email)
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={"detail": "Email already registered"}
        )
    
    try:
        user = user_crud.user.create(db, obj_in=user_data)
        users = user_crud.user.get_all(db)
        
        if templates:
            return templates.TemplateResponse("components/user_list.html", {
                "request": request,
                "users": users
            })
        return HTMLResponse(f"<p>User created: {user.name}</p>")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error creating user: {str(e)}"}
        )

@app.post("/news", response_class=HTMLResponse)
async def create_news_form(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    cover: str = Form(None),
    author_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Parse JSON content
        content_dict = json.loads(content)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON content"}
        )
    
    # Check if author exists and is verified
    author = user_crud.user.get(db, id=author_id)
    if not author:
        return JSONResponse(
            status_code=404,
            content={"detail": "Author not found"}
        )
    if not author.is_verified:
        return JSONResponse(
            status_code=403,
            content={"detail": "Author is not verified"}
        )
    
    try:
        news_data = NewsCreate(title=title, content=content_dict, cover=cover)
        news = news_crud.news.create(db, obj_in=news_data, author_id=author_id)
        news_list = news_crud.news.get_all(db)
        
        if templates:
            return templates.TemplateResponse("components/news_list.html", {
                "request": request,
                "news": news_list
            })
        return HTMLResponse(f"<p>News created: {news.title}</p>")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error creating news: {str(e)}"}
        )

@app.post("/comments", response_class=HTMLResponse)
async def create_comment_form(
    request: Request,
    text: str = Form(...),
    news_id: int = Form(...),
    author_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Check if news exists
    news = news_crud.news.get(db, id=news_id)
    if not news:
        return JSONResponse(
            status_code=404,
            content={"detail": "News not found"}
        )
    
    # Check if author exists
    author = user_crud.user.get(db, id=author_id)
    if not author:
        return JSONResponse(
            status_code=404,
            content={"detail": "Author not found"}
        )
    
    try:
        comment_data = CommentCreate(text=text)
        comment = comment_crud.comment.create(db, obj_in=comment_data, news_id=news_id, author_id=author_id)
        comments = comment_crud.comment.get_all(db)
        
        if templates:
            return templates.TemplateResponse("components/comment_list.html", {
                "request": request,
                "comments": comments
            })
        return HTMLResponse(f"<p>Comment created by {author.name}</p>")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error creating comment: {str(e)}"}
        )

# Delete operations for HTMX
@app.delete("/users/{user_id}")
async def delete_user_html(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.user.get(db, id=user_id)
    if not user:
        return JSONResponse(
            status_code=404,
            content={"detail": "User not found"}
        )
    
    try:
        user_crud.user.delete(db, id=user_id)
        return JSONResponse(content={"message": "User deleted successfully"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error deleting user: {str(e)}"}
        )

@app.delete("/news/{news_id}")
async def delete_news_html(news_id: int, db: Session = Depends(get_db)):
    news = news_crud.news.get(db, id=news_id)
    if not news:
        return JSONResponse(
            status_code=404,
            content={"detail": "News not found"}
        )
    
    try:
        news_crud.news.delete(db, id=news_id)
        return JSONResponse(content={"message": "News deleted successfully"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error deleting news: {str(e)}"}
        )

@app.delete("/comments/{comment_id}")
async def delete_comment_html(comment_id: int, db: Session = Depends(get_db)):
    comment = comment_crud.comment.get(db, id=comment_id)
    if not comment:
        return JSONResponse(
            status_code=404,
            content={"detail": "Comment not found"}
        )
    
    try:
        comment_crud.comment.delete(db, id=comment_id)
        return JSONResponse(content={"message": "Comment deleted successfully"})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error deleting comment: {str(e)}"}
        )

# Include your existing API routers
from app.api.routes import users, news, comments

app.include_router(users.router, prefix="/api/routes/users", tags=["users-api"])
app.include_router(news.router, prefix="/api/routes/news", tags=["news-api"])
app.include_router(comments.router, prefix="/api/routes/comments", tags=["comments-api"])

@app.get("/")
def read_root():
    return {"message": "Welcome to News CRUD API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

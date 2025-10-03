from fastapi import FastAPI
from app.api.routes import users, news, comments
from app.database.session import engine
from app.models import base

# Create tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="News CRUD API", version="1.0.0")

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(news.router, prefix="/news", tags=["news"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to News CRUD API"}

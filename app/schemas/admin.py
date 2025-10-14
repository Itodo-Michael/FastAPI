from pydantic import BaseModel
from typing import List
from datetime import datetime

class AdminStats(BaseModel):
    total_users: int
    total_news: int
    total_comments: int
    admin_users: int
    verified_users: int
    regular_users: int

class UserUpdateAdmin(BaseModel):
    is_verified: bool = None
    is_admin: bool = None
    is_active: bool = None
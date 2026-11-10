from pydantic import BaseModel, EmailStr
from datetime import datetime


class PostBase(BaseModel):
    id: int
    content: str
    published: bool = True


class Post(BaseModel):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

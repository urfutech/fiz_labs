from pydantic import BaseModel, EmailStr, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

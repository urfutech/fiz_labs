from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class Student(BaseModel):
    name: str


class Teacher(BaseModel):
    name: str


class Lab(BaseModel):
    title: str
    description: str
    is_published: bool


class LabCreate(Lab):
    created_by: int | None = None


class LabUpdate(Lab):
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    email: str
    role: str


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

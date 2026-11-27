from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class Lab(BaseModel):
    title: str
    description: str
    is_published: bool


class LabCreate(Lab):
    created_by: int | None = None


class LabUpdate(Lab):
    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseModel):
    role: str
    login: str
    password: str
    first_name: str
    last_name: str
    middle_name: str


class User(BaseModel):
    role: str
    login: str
    first_name: str
    last_name: str
    middle_name: str
    password_hash: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class Group(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class TeacherLogin(User):
    selectable_for_students: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str

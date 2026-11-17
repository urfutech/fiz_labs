from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models, utils
from .db_sqlalchemy import engine, get_db
from .models import Post

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

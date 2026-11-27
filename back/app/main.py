from fastapi import FastAPI, Depends, Body
from typing import Annotated

# from .routers import auth, lab, user, group
from .routers import user

# from . import oauth2
from .database import get_db
from sqlalchemy.orm import Session

from . import models, schemas

app = FastAPI()

# app.include_router(auth.router)
# app.include_router(lab.router)
app.include_router(user.router)
# app.include_router(oauth2.router)
# app.include_router(group.router)


# @app.get("/")
# def get_users(db: Session = Depends(get_db)):
#     users = db.query(models.Users).all()
#     return [schemas.User.model_validate(u).model_dump() for u in users]


# @app.post("/")
# def create_user(user: schemas.User, db: Session = Depends(get_db)):
#     new_user = models.Users(**user.model_dump())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"data": new_user}


# def pipa(db: Session = Depends(get_db)):
#     db.query(models.LLLLLL).filter(LLLL).all()
#     return

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from .. import oauth2


router = APIRouter(prefix="/users")


def create_user_to_User(create_user: schemas.CreateUser):
    return schemas.User(
        role=create_user.role,
        login=create_user.login,
        first_name=create_user.first_name,
        last_name=create_user.last_name,
        middle_name=create_user.middle_name,
        password_hash=oauth2.get_password_hash(create_user.password),
        status="active",
    )


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.Users).all()
    return [schemas.User.model_validate(u).model_dump() for u in users]


@router.get("/")
def get_user(login: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.login == login).first()
    return schemas.User.model_validate(user)


@router.post("/")
def create_user(create_user: schemas.CreateUser, db: Session = Depends(get_db)):
    user_scheme = create_user_to_User(create_user)
    new_user = models.Users(**user_scheme.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"data": oauth2.get_user(user_scheme.login, db)}


@router.delete("/")
def delete_user(login: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.login == login).first()
    db.delete(user)
    db.commit()
    return True


@router.get("/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    user = oauth2.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = oauth2.timedelta(minutes=oauth2.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        schemas.TokenData(email=user.login),
        expires_delta=access_token_expires,
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


# db: Session = Depends(get_db)
# print(get_users(db))

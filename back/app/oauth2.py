from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .database import get_db
from . import schemas, models


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "b1472ce5d54494eee8e1119235c89b9583bc5c466737adffddbec919f2022223"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(login: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.login == login).first()
    if not user:
        raise Exception("no winning")
    return schemas.User.model_validate(user)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user(username, db)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(
    data: schemas.TokenData, expires_delta: timedelta | None = None
):
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # if not token:
    #     return RedirectResponse(url="/login", status_code=202)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("email")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_active(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    if current_user.status == "not active":
        raise HTTPException(status_code=400, detail="Not active user")
    return current_user


@router.post("/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        schemas.TokenData(email=user.login),
        expires_delta=access_token_expires,
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid data"
        )
    if not utils.verify(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid data"
        )

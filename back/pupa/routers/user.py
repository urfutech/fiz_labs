from fastapi import Depends, HTTPException, APIRouter
from .. import models, schemas, utils
from ..db_sqlalchemy import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/users", status_code=201, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = utils.hash(user.password)
    user.password = hashed
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"user with {id} was not found")
    return user

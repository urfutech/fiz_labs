from fastapi import Depends, HTTPException, APIRouter
from .. import models, schemas
from ..db_sqlalchemy import get_db
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": "success"}


@router.get("/posts/{post_id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    return {"post": post}


@router.post("/posts", status_code=201)
def create_posts(post: schemas.Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@router.delete("/posts/{post_id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404)
    post.delete(synchronize_session=False)
    db.commit()


@router.put("/posts/{post_id}")
def update_post(id: int, updated_post: models.Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=404)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

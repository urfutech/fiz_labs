from fastAPI import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
from . import models
from .database import engine, get_db
from .models import Post

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": "success"}


@app.get("/posts/{post_id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    return {"post": post}


@app.post("/posts", status_code=201)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.delete("/posts/{post_id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404)
    post.delete(synchronize_session=False)
    db.commit()


@app.put("/posts/{post_id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=404)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()


@app.post("/users", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

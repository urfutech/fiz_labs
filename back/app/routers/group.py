from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/groups")


@router.get("")
def get_groups(db: Session = Depends(get_db)):
    groups = db.query(models.Groups).all()
    return [schemas.Group.model_validate(g) for g in groups]


@router.post("")
def create_group(group: schemas.Group, db: Session = Depends(get_db)):
    new_group = models.Groups(**group.model_dump())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return get_groups(db)


@router.delete("")
def delete_group(group: schemas.Group, db: Session = Depends(get_db)):
    group_row = db.query(models.Groups).filter(models.Groups.name == group.name).first()
    db.delete(group_row)
    db.commit()
    return get_groups(db)

from .. import models, schemas
from typing import List
from ..database import get_db
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(prefix="/labs", tags=["labs"])


@router.get("/{lab_id}")
def get_lab(id: int, db: Session = Depends(get_db)):
    lab = db.query(models.Lab).filter(models.Lab.id == id).first()
    return {"lab": lab}


@router.get("", response_model=schemas.Lab)
def get_labs(db: Session = Depends(get_db)):
    labs = db.query(models.Lab).all()
    return {"labs": labs}


@router.post("/create")
def create_lab(lab: schemas.LabCreate, db: Session = Depends(get_db)):
    new_lab = models.Lab(**lab.model_dump())
    db.add(new_lab)
    db.commit()
    db.refresh(new_lab)
    return {"data": new_lab}


@router.delete("")
def delete_lab(id: int, db: Session = Depends(get_db)):
    lab = db.query(models.Lab).filter(models.Lab.id == id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="lab not found")
    lab.delete(synchronize_session=False)
    db.commit()


@router.put("/{id}")
def update_lab(id: int, up_lab: schemas.LabUpdate, db: Session = Depends(get_db)):
    lab_query = db.query(models.Lab).filter(models.Lab.id == id)
    lab = lab_query.first()
    if not lab:
        raise HTTPException(status_code=404, detail="lab not found")
    lab_query.update(up_lab.model_dump(), synchronize_session=False)
    db.commit()

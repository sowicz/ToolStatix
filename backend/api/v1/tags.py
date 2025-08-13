from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.orm import Session
from db.schemas import schema
from db.models import main_tags
from db.database import get_db
from validators.validators import MachineTagValidator



router = APIRouter()


@router.post("/add-tag", response_model=schema.MainTagsRead)
def create_tag(tag: schema.MainTagsCreate, db: Session = Depends(get_db)):
    try:
        MachineTagValidator(db).validate(tag)
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e))
    db_tag = main_tags.MainTags(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/tags", response_model=List[schema.MainTagsRead])
def list_tags(db: Session = Depends(get_db)):
    return db.query(main_tags.MainTags).all()
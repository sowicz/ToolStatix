from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.orm import Session
from db.schemas import schema
from db.models import related_tags, main_tags
from db.database import get_db
from validators.validators import RelatedTagValidator



router = APIRouter()


@router.post("/add-related-tag", response_model=schema.RelatedTagsBase)
def create_related_tag(related_tag: schema.RelatedTagsCreate, db: Session = Depends(get_db)):
    # Check if main_tag exist
    main_tag = db.query(main_tags.MainTags).filter(main_tags.MainTags.id == related_tag.main_tag_id).first()
    if not main_tag:
        raise HTTPException(status_code=404, detail="Main tag not found")

    db_tag = related_tags.RelatedTags(**related_tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/related-tags", response_model=List[schema.RelatedTagsBase])
def list_tags(db: Session = Depends(get_db)):
    return db.query(related_tags.RelatedTags).all()
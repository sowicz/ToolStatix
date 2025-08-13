from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import network_data_source_model
from db.schemas import schema
from validators.validators import DataSourceValidator


router = APIRouter()


@router.post("/network-data-sources", response_model=schema.NetworkDataSourceRead)
def create_data_source(data: schema.NetworkDataSourceCreate, db: Session = Depends(get_db)):
    try:
        DataSourceValidator(db).validate(data)
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e))

    db_data_source = network_data_source_model.NetworkDataSource(**data.model_dump())

    db.add(db_data_source)
    db.commit()
    db.refresh(db_data_source)
    return db_data_source


@router.get("/network-data-sources", response_model=List[schema.NetworkDataSourceRead])
def list_data_sources(db: Session = Depends(get_db)):
    return db.query(network_data_source_model.NetworkDataSource).all()
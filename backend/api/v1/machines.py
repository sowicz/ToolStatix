from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.schemas import schema
from db.models import machines_model
from db.database import get_db

router = APIRouter()


@router.post("/machines", response_model=schema.MachinesRead)
def create_machine(machine: schema.MachinesCreate, db: Session = Depends(get_db)):
    db_machine = machines_model.Machines(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


@router.get("/machines", response_model=List[schema.MachinesRead])
def list_machines(db: Session = Depends(get_db)):
    return db.query(machines_model.Machines).all()



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.schemas import schema  
from db.database import get_db
from db.models import tags_data
from drivers.report.generate_report import export_to_excel

router = APIRouter()


@router.get("/report/{main_tag_id}")
def export_excel_report(main_tag_id: int, db: Session = Depends(get_db)):
    records: List[tags_data.TagsData] = db.query(tags_data.TagsData).filter(tags_data.TagsData.main_tag_id == main_tag_id).all()

    if not records:
        raise HTTPException(status_code=404, detail="Brak danych dla tego main_tag_id")

    tag_data = [
        schema.TagStatsResponse(
            tag_name=record.tag_name,
            min=record.min,
            max=record.max,
            avg=record.avg,
            work_time=record.work_time
        )
        for record in records
    ]

    filepath = export_to_excel(tag_data)

    return {"message": "Raport wygenerowany", "filepath": filepath}
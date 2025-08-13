import pandas as pd
from db.schemas import schema
from datetime import datetime
import os


def export_to_excel(tag_data: list[schema.TagStatsResponse]):
    # Grupowanie po tag_name
    grouped = {}
    for row in tag_data:
        grouped.setdefault(row.tag_name, []).append(row)

    # Ścieżka do pliku
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.xlsx"
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Tworzenie Excela
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        for tag_name, rows in grouped.items():
            df = pd.DataFrame([{
                "min": r.min,
                "max": r.max,
                "avg": r.avg,
                "work_time": r.work_time
            } for r in rows])

            df.to_excel(writer, sheet_name=tag_name[:31], index=False)  # max 31 znaków

    return filepath
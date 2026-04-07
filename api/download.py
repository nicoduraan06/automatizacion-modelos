from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
from io import BytesIO

from src.storage.factory import get_storage
from src.services.report_exporter import ReportExporter

router = APIRouter()

storage = get_storage()


@router.get("/download")
def download_report(process_id: str = Query(...)):
    try:
        result_key = f"{process_id}/result.json"

        try:
            result_bytes = storage.read_bytes(result_key)
        except Exception:
            raise FileNotFoundError("No existe resultado procesado")

        result_data = json.loads(result_bytes.decode("utf-8"))

        exporter = ReportExporter()

        excel_bytes = exporter.build_excel_report(
            process_id=process_id,
            model_key=result_data.get("model_detected"),
            mapped_results=result_data.get("mapped_results", {}),
            traceability=result_data.get("traceability", {}),
            validation=result_data.get("validation", {}),
            pdf_data=result_data.get("pdf_data"),
        )

        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="reporte_{process_id}.xlsx"'
            },
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No existe resultado procesado")

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando descarga: {exc}"
        )
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from src.services.export_service import ExportService
from src.services.process_service import ProcessService

app = FastAPI(title="modelo303-download")
process_service = ProcessService()
export_service = ExportService()


@app.get("/")
def download(process_id: str = Query(...), kind: str = Query("excel")):
    try:
        result = process_service.load_result(process_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    if kind == "excel":
        content = export_service.to_excel_bytes(result)
        headers = {"Content-Disposition": f'attachment; filename="resultado_{process_id}.xlsx"'}
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )
    if kind == "json":
        headers = {"Content-Disposition": f'attachment; filename="resultado_{process_id}.json"'}
        return Response(
            content=result.model_dump_json(indent=2),
            media_type="application/json",
            headers=headers,
        )
    raise HTTPException(status_code=400, detail="kind debe ser 'excel' o 'json'")

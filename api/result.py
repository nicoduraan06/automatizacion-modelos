from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from src.services.process_service import ProcessService

app = FastAPI(title="modelo303-result")
service = ProcessService()


@app.get("/")
def result(process_id: str = Query(...)):
    try:
        data = service.load_result(process_id)
        return data.model_dump()
    except FileNotFoundError:
        try:
            manifest = service.load_manifest(process_id)
            return {
                "process_id": process_id,
                "status": manifest.status,
                "message": "Todavía no hay resultado procesado para este proceso"
            }
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="No existe el proceso indicado")

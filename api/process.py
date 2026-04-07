from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.process_service import ProcessService

router = APIRouter()

service = ProcessService()


class ProcessRequest(BaseModel):
    process_id: str


@router.post("/process")
def process(payload: ProcessRequest):
    try:
        result = service.process(payload.process_id)

        return {
            "process_id": result.process_id,
            "summary": result.summary,
            "validations": result.validations,
            "warnings": result.warnings,
            "boxes": [
                {
                    "code": b.box_code,
                    "excel": b.excel_value,
                    "pdf": b.pdf_value,
                    "status": b.status,
                }
                for b in result.box_results
            ]
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No existe el proceso indicado")

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando: {exc}"
        )
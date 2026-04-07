from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
import json

from src.storage.factory import get_storage

router = APIRouter()

storage = get_storage()


@router.get("/result")
def get_result(process_id: str = Query(...)):
    try:
        result_key = f"{process_id}/result.json"

        try:
            result_bytes = storage.read_bytes(result_key)
        except Exception:
            raise FileNotFoundError("No existe resultado para ese process_id")

        result_data = json.loads(result_bytes.decode("utf-8"))

        return {
            "process_id": process_id,
            "status": "completed",
            "data": result_data
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="No existe resultado para ese process_id"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo resultado: {exc}"
        )
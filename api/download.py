from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.storage.factory import get_storage

router = APIRouter()
storage = get_storage()


@router.get("/download")
def download(process_id: str = Query(...), kind: str = Query("json")):
    try:
        if kind == "json":
            key = f"{process_id}/result.json"
            content_type = "application/json"
            filename = "resultado.json"

        elif kind == "excel":
            key = f"{process_id}/result.xlsx"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "resultado.xlsx"

        else:
            raise HTTPException(status_code=400, detail="Tipo no válido")

        try:
            file_bytes = storage.read_bytes(key)
        except Exception:
            raise FileNotFoundError("Archivo no encontrado")

        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No existe el archivo solicitado")

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error descargando archivo: {exc}"
        )
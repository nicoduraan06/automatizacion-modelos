from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import List, Optional

from src.models.contracts import ProcessManifest, UploadedFileRef
from src.storage.factory import get_storage
from src.utils.common import new_process_id, safe_filename, utc_now_iso

router = APIRouter()

storage = get_storage()


@router.post("/upload")
async def upload(
    excel_file: UploadFile = File(...),
    pdf_files: Optional[List[UploadFile]] = File(default=None)
):
    try:
        # 🔧 Evita error cuando no se envían PDFs
        pdf_files = pdf_files or []

        # -------------------------
        # VALIDACIÓN EXCEL
        # -------------------------
        if not excel_file.filename.lower().endswith((".xlsx", ".xlsm", ".xls")):
            raise HTTPException(
                status_code=400,
                detail="El archivo Excel debe ser .xlsx, .xlsm o .xls"
            )

        # -------------------------
        # VALIDACIÓN PDFs
        # -------------------------
        for pdf in pdf_files:
            if not pdf.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo PDF inválido: {pdf.filename}"
                )

        # -------------------------
        # GENERAR PROCESS ID
        # -------------------------
        process_id = new_process_id()

        # -------------------------
        # GUARDAR EXCEL
        # -------------------------
        excel_bytes = await excel_file.read()
        excel_name = safe_filename(excel_file.filename)
        excel_key = f"{process_id}/input/{excel_name}"

        storage.write_bytes(excel_key, excel_bytes, excel_file.content_type)

        # -------------------------
        # GUARDAR PDFs
        # -------------------------
        pdf_refs: List[UploadedFileRef] = []

        for pdf in pdf_files:
            data = await pdf.read()
            pdf_name = safe_filename(pdf.filename)
            pdf_key = f"{process_id}/input/{pdf_name}"

            storage.write_bytes(pdf_key, data, pdf.content_type)

            pdf_refs.append(
                UploadedFileRef(
                    name=pdf_name,
                    storage_key=pdf_key,
                    content_type=pdf.content_type,
                    size_bytes=len(data),
                )
            )

        # -------------------------
        # CREAR MANIFEST
        # -------------------------
        manifest = ProcessManifest(
            process_id=process_id,
            created_at=utc_now_iso(),
            status="uploaded",
            excel=UploadedFileRef(
                name=excel_name,
                storage_key=excel_key,
                content_type=excel_file.content_type,
                size_bytes=len(excel_bytes),
            ),
            pdfs=pdf_refs,
            logs=["Carga completada correctamente"],
        )

        storage.write_bytes(
            f"{process_id}/manifest.json",
            manifest.model_dump_json(indent=2).encode("utf-8"),
            "application/json"
        )

        # -------------------------
        # RESPUESTA
        # -------------------------
        return {
            "process_id": process_id,
            "status": manifest.status,
            "excel": manifest.excel.model_dump(),
            "pdfs": [p.model_dump() for p in manifest.pdfs],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
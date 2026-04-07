from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

from src.parsers.excel_parser import ExcelParser
from src.parsers.pdf_parser import Pdf303Parser

from src.storage.factory import get_storage
from src.services.rule_engine import RuleEngine
from src.services.model_detector import ModelDetector
from src.services.model_loader import ModelLoader
from src.services.validator import Validator

router = APIRouter()

storage = get_storage()


class ProcessRequest(BaseModel):
    process_id: str


@router.post("/process")
def process(payload: ProcessRequest):
    try:
        process_id = payload.process_id

        manifest_key = f"{process_id}/manifest.json"

        try:
            manifest_bytes = storage.read_bytes(manifest_key)
        except Exception:
            raise FileNotFoundError("No existe el proceso indicado")

        manifest = json.loads(manifest_bytes.decode("utf-8"))

        # =========================
        # EXCEL
        # =========================
        excel_key = manifest["excel"]["storage_key"]
        excel_name = manifest["excel"]["name"]

        excel_bytes = storage.read_bytes(excel_key)

        parser = ExcelParser()
        excel_data = parser.parse_bytes(
            filename=excel_name,
            content=excel_bytes
        )

        all_cells = []
        for sheet, cells in excel_data.cell_index.items():
            for coord, data in cells.items():
                all_cells.append({
                    "sheet": sheet,
                    "cell": coord,
                    "value": data["value"],
                    "formula": data["formula"]
                })

        # =========================
        # PDF
        # =========================
        pdf_data = None
        model_from_pdf = None

        if manifest.get("pdfs"):
            pdf_key = manifest["pdfs"][0]["storage_key"]
            pdf_bytes = storage.read_bytes(pdf_key)

            pdf_parser = Pdf303Parser()
            pdf_data = pdf_parser.parse_bytes(pdf_bytes)

            model_from_pdf = pdf_data.get("model_key")

        # =========================
        # DETECCIÓN MODELO
        # =========================
        if model_from_pdf and model_from_pdf != "unknown":
            model_key = model_from_pdf
        else:
            detector = ModelDetector()
            model_key = detector.detect(all_cells)

        if model_key == "unknown":
            raise ValueError("No se ha podido detectar el modelo automáticamente")

        # =========================
        # CARGA MODELO
        # =========================
        loader = ModelLoader()
        model_definition = loader.load(model_key)

        # =========================
        # RULE ENGINE
        # =========================
        engine = RuleEngine(model_definition)
        traceability = engine.apply(all_cells)

        mapped_results = {
            k: v["value"] for k, v in traceability.items()
        }

        # =========================
        # VALIDACIÓN
        # =========================
        validator = Validator()
        validation_result = validator.validate(traceability, pdf_data)

        # =========================
        # RESPUESTA FINAL
        # =========================
        response_payload = {
            "process_id": process_id,
            "model_detected": model_key,
            "pdf_data": pdf_data,
            "sheets_detected": excel_data.sheets_used,
            "total_cells": len(all_cells),
            "sample_cells": all_cells[:20],
            "mapped_results": mapped_results,
            "traceability": traceability,
            "validation": validation_result
        }

        # 🔥 GUARDAR RESULTADO (CLAVE)
        storage.write_bytes(
            f"{process_id}/result.json",
            json.dumps(response_payload, ensure_ascii=False, indent=2, default=str).encode("utf-8"),
            "application/json"
        )

        return response_payload

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No existe el proceso indicado")

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el expediente: {exc}"
        )
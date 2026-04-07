from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

from src.parsers.excel_parser import ExcelParser
from src.storage.factory import get_storage
from src.services.rule_engine import RuleEngine  # 🔥 NUEVO

router = APIRouter()

storage = get_storage()


class ProcessRequest(BaseModel):
    process_id: str


@router.post("/process")
def process(payload: ProcessRequest):
    try:
        process_id = payload.process_id

        # 🔹 Leer manifest
        manifest_key = f"{process_id}/manifest.json"

        try:
            manifest_bytes = storage.read_bytes(manifest_key)
        except Exception:
            raise FileNotFoundError("No existe el proceso indicado")

        manifest = json.loads(manifest_bytes.decode("utf-8"))

        # 🔹 Leer Excel desde storage
        excel_key = manifest["excel"]["storage_key"]
        excel_name = manifest["excel"]["name"]

        excel_bytes = storage.read_bytes(excel_key)

        # 🔹 Parsear Excel
        parser = ExcelParser()

        excel_data = parser.parse_bytes(
            filename=excel_name,
            content=excel_bytes
        )

        # 🔹 Convertir a lista de celdas
        all_cells = []
        for sheet, cells in excel_data.cell_index.items():
            for coord, data in cells.items():
                all_cells.append({
                    "sheet": sheet,
                    "cell": coord,
                    "value": data["value"],
                    "formula": data["formula"]
                })

        # =========================================================
        # 🔥 NUEVO: RULE ENGINE
        # =========================================================

        # 🔹 Cargar configuración del modelo (TU JSON)
        with open("src/mappings/modelo303_rules.json", "r", encoding="utf-8") as f:
            model_definition = json.load(f)

        # 🔹 Ejecutar motor de reglas
        engine = RuleEngine(model_definition)
        mapped_results = engine.apply(all_cells)

        # =========================================================

        return {
            "process_id": process_id,
            "sheets_detected": excel_data.sheets_used,
            "total_cells": len(all_cells),
            "sample_cells": all_cells[:20],

            # 🔥 NUEVO RESULTADO INTELIGENTE
            "mapped_results": mapped_results
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No existe el proceso indicado")

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el expediente: {exc}"
        )
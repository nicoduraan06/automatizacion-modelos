from __future__ import annotations

from io import BytesIO

import pandas as pd

from src.models.contracts import ProcessResult


class ExportService:
    def to_excel_bytes(self, result: ProcessResult) -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pd.DataFrame([{
                "process_id": result.process_id,
                "nif_pdf": result.pdf_data[0].nif if result.pdf_data else None,
                "periodo_pdf": result.pdf_data[0].period if result.pdf_data else None,
                "ejercicio_pdf": result.pdf_data[0].fiscal_year if result.pdf_data else None,
                "advertencias": " | ".join(result.warnings),
                "validaciones": " | ".join(result.validations),
            }]).to_excel(writer, sheet_name="Resumen", index=False)

            box_rows = []
            for item in result.box_results:
                box_rows.append({
                    "Casilla": item.box_code,
                    "Descripción": item.description,
                    "Valor Excel": item.excel_value,
                    "Valor PDF": item.pdf_value,
                    "Diferencia": item.difference,
                    "Estado": item.status,
                    "Regla": item.rule_name,
                    "Evidencia": " | ".join([f"{e.sheet}!{e.cell}={e.value}" for e in item.evidence]),
                })
            pd.DataFrame(box_rows).to_excel(writer, sheet_name="Casillas", index=False)
        return output.getvalue()

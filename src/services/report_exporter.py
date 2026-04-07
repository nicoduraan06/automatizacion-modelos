from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd


class ReportExporter:
    def build_excel_report(
        self,
        process_id: str,
        model_key: str,
        mapped_results: dict[str, Any],
        traceability: dict[str, Any],
        validation: dict[str, Any],
        pdf_data: dict[str, Any] | None = None,
    ) -> bytes:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            self._write_summary(
                writer=writer,
                process_id=process_id,
                model_key=model_key,
                mapped_results=mapped_results,
                validation=validation,
                pdf_data=pdf_data,
            )

            self._write_results(
                writer=writer,
                mapped_results=mapped_results,
            )

            self._write_validation(
                writer=writer,
                validation=validation,
            )

            self._write_traceability(
                writer=writer,
                traceability=traceability,
            )

        output.seek(0)
        return output.read()

    def _write_summary(
        self,
        writer,
        process_id: str,
        model_key: str,
        mapped_results: dict[str, Any],
        validation: dict[str, Any],
        pdf_data: dict[str, Any] | None = None,
    ) -> None:
        rows = [
            {"campo": "process_id", "valor": process_id},
            {"campo": "modelo_detectado", "valor": model_key},
            {"campo": "estado_validacion", "valor": validation.get("status")},
            {"campo": "numero_resultados", "valor": len(mapped_results)},
        ]

        if pdf_data:
            rows.extend([
                {"campo": "pdf_nif", "valor": pdf_data.get("nif")},
                {"campo": "pdf_ejercicio", "valor": pdf_data.get("fiscal_year")},
                {"campo": "pdf_periodo", "valor": pdf_data.get("period")},
                {"campo": "pdf_tipo_declaracion", "valor": pdf_data.get("declaration_type")},
                {"campo": "pdf_justificante", "valor": pdf_data.get("reference_number")},
            ])

        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name="Resumen", index=False)

    def _write_results(
        self,
        writer,
        mapped_results: dict[str, Any],
    ) -> None:
        rows = []

        for field_key, value in mapped_results.items():
            rows.append({
                "campo": field_key,
                "valor": value,
            })

        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name="Resultados", index=False)

    def _write_validation(
        self,
        writer,
        validation: dict[str, Any],
    ) -> None:
        differences = validation.get("differences", [])

        if not differences:
            df = pd.DataFrame([{
                "estado": validation.get("status"),
                "mensaje": validation.get("message", "Sin diferencias detectadas"),
            }])
        else:
            df = pd.DataFrame(differences)

        df.to_excel(writer, sheet_name="Validacion", index=False)

    def _write_traceability(
        self,
        writer,
        traceability: dict[str, Any],
    ) -> None:
        rows = []

        for field_key, field_data in traceability.items():
            value = field_data.get("value")
            sources = field_data.get("sources", [])

            if not sources:
                rows.append({
                    "campo": field_key,
                    "valor_calculado": value,
                    "sheet": None,
                    "cell": None,
                    "valor_origen": None,
                })
                continue

            for source in sources:
                rows.append({
                    "campo": field_key,
                    "valor_calculado": value,
                    "sheet": source.get("sheet"),
                    "cell": source.get("cell"),
                    "valor_origen": source.get("value"),
                })

        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name="Trazabilidad", index=False)
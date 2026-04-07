from typing import Dict, Any


class Validator:

    def validate(self, mapped_results: Dict[str, Any], pdf_data: Dict[str, Any]) -> Dict:

        if not pdf_data:
            return {
                "status": "no_pdf",
                "differences": [],
                "message": "No se ha proporcionado PDF para validación"
            }

        pdf_boxes = pdf_data.get("boxes", {})

        differences = []

        for field_key, field_data in mapped_results.items():

            # 🔥 ahora usamos estructura con trazabilidad
            value = field_data["value"]

            # 🔹 intentar mapear a casilla
            box_code = self._map_field_to_box(field_key)

            if not box_code:
                continue

            pdf_value = pdf_boxes.get(box_code)

            if pdf_value is None:
                differences.append({
                    "field": field_key,
                    "box": box_code,
                    "issue": "missing_in_pdf",
                    "excel_value": value,
                    "pdf_value": None
                })
                continue

            if abs(value - pdf_value) > 0.01:
                differences.append({
                    "field": field_key,
                    "box": box_code,
                    "issue": "mismatch",
                    "excel_value": value,
                    "pdf_value": pdf_value,
                    "difference": value - pdf_value
                })

        status = "ok" if not differences else "warning"

        return {
            "status": status,
            "differences": differences
        }

    def _map_field_to_box(self, field_key: str) -> str | None:

        mapping = {
            "base_imponible_general": "001",
            "cuota_devengada_general": "003",
            "iva_deducible": "028",
            "resultado_final": "070"
        }

        return mapping.get(field_key)
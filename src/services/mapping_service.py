from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.contracts import BoxResult, Excel303Data, Pdf303Data, TraceCell
from src.utils.common import round2


class MappingService:
    def __init__(self, rules_path: str | None = None):
        default_path = Path(__file__).resolve().parent.parent / "mappings" / "modelo303_rules.json"
        self.rules_path = Path(rules_path or default_path)

        data = json.loads(self.rules_path.read_text(encoding="utf-8"))

        if "fields" in data:
            self.rules = data["fields"]
        elif "rules" in data:
            self.rules = data["rules"]
        else:
            raise ValueError("El JSON de reglas no contiene 'fields' ni 'rules'")

    def _cell_value(self, excel_data: Excel303Data, sheet: str, cell: str) -> tuple[float | None, TraceCell]:
        entry = excel_data.cell_index.get(sheet, {}).get(cell, {})
        value = entry.get("value")
        trace = TraceCell(sheet=sheet, cell=cell, value=value, formula=entry.get("formula"))

        if value in (None, ""):
            return None, trace

        try:
            return float(value), trace
        except Exception:
            return None, trace

    def _eval_formula(self, expression: str, computed: dict[str, float | None]) -> float | None:
        try:
            return round2(eval(expression, {"__builtins__": {}}, computed))
        except Exception:
            return None

    def compute(self, excel_data: Excel303Data, pdf_reference: Pdf303Data | dict | None) -> list[BoxResult]:
        results: list[BoxResult] = []
        computed: dict[str, float | None] = {}

        # 🔥 FIX CLAVE AQUÍ
        if pdf_reference is None:
            pdf_boxes = {}
        elif isinstance(pdf_reference, dict):
            pdf_boxes = pdf_reference.get("boxes", {})
        else:
            pdf_boxes = getattr(pdf_reference, "boxes", {})

        for rule in self.rules:
            evidence: list[TraceCell] = []
            excel_value: float | None = None

            rule_def = rule.get("rule", {})
            rtype = rule_def.get("type")

            # =========================
            # MOTOR
            # =========================

            if rtype == "label_match_sum":
                total = 0.0

                for sheet, cells in excel_data.cell_index.items():
                    for coord, data in cells.items():
                        val = data.get("value")

                        if isinstance(val, (int, float)):
                            total += float(val)

                excel_value = round2(total)

            elif rtype == "formula":
                expression = rule_def.get("expression", "")
                excel_value = self._eval_formula(expression, computed)

            else:
                excel_value = None

            # =========================
            # RESULTADO
            # =========================

            box_code = str(rule.get("box_code")).zfill(3)

            computed[rule["key"]] = excel_value

            pdf_value = pdf_boxes.get(box_code)

            difference = None
            if excel_value is not None and pdf_value is not None:
                difference = round2(excel_value - pdf_value)

            # 🔹 STATUS
            if excel_value is None and pdf_value is None:
                status = "missing"
            elif excel_value is not None and pdf_value is None:
                status = "warning"
            elif excel_value is None and pdf_value is not None:
                status = "missing"
            else:
                status = "ok" if abs(difference or 0) < 0.01 else "mismatch"

            results.append(
                BoxResult(
                    box_code=box_code,
                    description=rule.get("description"),
                    excel_value=excel_value,
                    pdf_value=pdf_value,
                    difference=difference,
                    status=status,
                    rule_name=rule.get("key"),
                    evidence=evidence,
                )
            )

        return results
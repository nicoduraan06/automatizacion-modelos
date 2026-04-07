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
        self.rules = json.loads(self.rules_path.read_text(encoding="utf-8"))["rules"]

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

    def _eval_formula(self, expression: str, already_computed: dict[str, float | None]) -> float | None:
        def box(code: str) -> float:
            value = already_computed.get(code)
            return float(value or 0)

        return round2(eval(expression, {"__builtins__": {}}, {"box": box}))

    def compute(self, excel_data: Excel303Data, pdf_reference: Pdf303Data | None) -> list[BoxResult]:
        results: list[BoxResult] = []
        computed: dict[str, float | None] = {}
        pdf_boxes = pdf_reference.boxes if pdf_reference else {}

        for rule in self.rules:
            evidence: list[TraceCell] = []
            excel_value: float | None = None
            rtype = rule["type"]

            if rtype == "sum_cells":
                total = 0.0
                for item in rule.get("cells", []):
                    value, trace = self._cell_value(excel_data, item["sheet"], item["cell"])
                    evidence.append(trace)
                    total += value or 0.0
                excel_value = round2(total)
            elif rtype == "direct_cell":
                value, trace = self._cell_value(excel_data, rule["sheet"], rule["cell"])
                evidence.append(trace)
                excel_value = round2(value)
            elif rtype == "formula":
                excel_value = self._eval_formula(rule["expression"], computed)
            else:
                excel_value = None

            box_code = str(rule["box_code"]).zfill(3)
            computed[box_code] = excel_value
            pdf_value = pdf_boxes.get(box_code)
            difference = None if excel_value is None or pdf_value is None else round2(excel_value - pdf_value)

            status = "missing"
            if excel_value is not None and pdf_value is None:
                status = "warning"
            elif excel_value is None and pdf_value is not None:
                status = "missing"
            elif excel_value is not None and pdf_value is not None:
                status = "ok" if abs((difference or 0)) < 0.01 else "mismatch"

            results.append(
                BoxResult(
                    box_code=box_code,
                    description=rule.get("description"),
                    excel_value=excel_value,
                    pdf_value=pdf_value,
                    difference=difference,
                    status=status,
                    rule_name=rule["rule_name"],
                    evidence=evidence,
                )
            )
        return results

from typing import List, Dict, Any
import re


class RuleEngine:
    def __init__(self, model_definition: Dict[str, Any]):
        self.model_definition = model_definition

    def apply(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = {}

        fields = self.model_definition.get("fields", [])

        # 🔹 Primera pasada: reglas simples
        for field in fields:
            key = field["key"]
            rule = field.get("rule", {})
            rule_type = rule.get("type")

            if rule_type == "label_match_sum":
                hints = field.get("source_hints", [])
                values = self._find_matches(cells, hints)
                results[key] = sum(values)

        # 🔹 Segunda pasada: fórmulas
        for field in fields:
            key = field["key"]
            rule = field.get("rule", {})
            rule_type = rule.get("type")

            if rule_type == "formula":
                expression = rule.get("expression")
                results[key] = self._evaluate_formula(expression, results)

        return results

    def _find_matches(self, cells: List[Dict[str, Any]], hints: List[str]) -> List[float]:
        values = []

        for cell in cells:
            value = cell.get("value")

            if isinstance(value, str):
                for hint in hints:
                    if hint.lower() in value.lower():
                        numeric = self._extract_number(value)
                        if numeric is not None:
                            values.append(numeric)

            elif isinstance(value, (int, float)):
                values.append(value)

        return values

    def _extract_number(self, text: str):
        match = re.search(r"[-+]?\d*\.\d+|\d+", text.replace(",", "."))
        if match:
            return float(match.group())
        return None

    def _evaluate_formula(self, expression: str, context: Dict[str, Any]):
        try:
            return eval(expression, {}, context)
        except Exception:
            return None
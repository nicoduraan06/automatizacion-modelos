from typing import List, Dict, Any
import re


class RuleEngine:
    def __init__(self, model_definition: Dict[str, Any]):
        self.model_definition = model_definition

    def apply(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = {}

        fields = self.model_definition.get("fields", [])

        # 🔹 Primera pasada
        for field in fields:
            key = field["key"]
            rule = field.get("rule", {})
            rule_type = rule.get("type")

            if rule_type == "label_match_sum":
                hints = field.get("source_hints", [])
                matches = self._find_matches(cells, hints)

                total = sum(m["value"] for m in matches)

                results[key] = {
                    "value": total,
                    "sources": matches
                }

        # 🔹 Segunda pasada (fórmulas)
        for field in fields:
            key = field["key"]
            rule = field.get("rule", {})
            rule_type = rule.get("type")

            if rule_type == "formula":
                expression = rule.get("expression")

                context = {
                    k: v["value"] if isinstance(v, dict) else v
                    for k, v in results.items()
                }

                value = self._evaluate_formula(expression, context)

                results[key] = {
                    "value": value,
                    "sources": []  # luego lo mejoraremos
                }

        return results

    def _find_matches(self, cells: List[Dict[str, Any]], hints: List[str]) -> List[Dict]:
        matches = []

        for cell in cells:
            value = cell.get("value")

            if isinstance(value, str):
                for hint in hints:
                    if hint.lower() in value.lower():
                        numeric = self._extract_number(value)
                        if numeric is not None:
                            matches.append({
                                "sheet": cell["sheet"],
                                "cell": cell["cell"],
                                "value": numeric
                            })

            elif isinstance(value, (int, float)):
                matches.append({
                    "sheet": cell["sheet"],
                    "cell": cell["cell"],
                    "value": float(value)
                })

        return matches

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
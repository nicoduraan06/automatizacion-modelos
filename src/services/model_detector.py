from typing import List, Dict


class ModelDetector:

    def detect(self, cells: List[Dict]) -> str:
        text_blob = self._build_text_blob(cells)

        # 🔥 reglas simples (mejoraremos luego)
        if "303" in text_blob and "iva" in text_blob:
            return "modelo303"

        if "111" in text_blob and "retenciones" in text_blob:
            return "modelo111"

        return "unknown"

    def _build_text_blob(self, cells: List[Dict]) -> str:
        texts = []

        for cell in cells:
            value = cell.get("value")

            if isinstance(value, str):
                texts.append(value.lower())

        return " ".join(texts)
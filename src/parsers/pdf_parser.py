from __future__ import annotations

import re
from io import BytesIO

import pdfplumber

from src.models.contracts import Pdf303Data

NIF_RE = re.compile(r"\b([A-Z0-9]\d{7}[A-Z0-9])\b")
PERIOD_RE = re.compile(r"(?:Periodo|PERIODO)\s*[:\-]?\s*(1T|2T|3T|01|02|03|04|05|06|07|08|09|10|11|12)")
YEAR_RE = re.compile(r"(?:Ejercicio|EJERCICIO)\s*[:\-]?\s*(20\d{2})")
JUST_RE = re.compile(r"(?:Número de justificante|Justificante)\s*[:\-]?\s*(\d{6,20})")
PREV_JUST_RE = re.compile(r"(?:justificante anterior|número justificante anterior)\s*[:\-]?\s*(\d{6,20})", re.I)
BOX_RE = re.compile(r"\(?([0-9]{2,3})\)?\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})")


class Pdf303Parser:

    def parse_bytes(self, content: bytes) -> dict:
        text_chunks: list[str] = []

        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")

        full_text = "\n".join(text_chunks)

        # =========================================================
        # 🔹 DETECTAR MODELO (NUEVO)
        # =========================================================
        model_key = "unknown"

        if "303" in full_text:
            model_key = "modelo303"

        # =========================================================
        # 🔹 EXTRAER CASILLAS
        # =========================================================
        boxes: dict[str, float] = {}

        for box_code, amount in BOX_RE.findall(full_text):
            normalized = float(amount.replace(".", "").replace(",", "."))
            boxes[box_code.zfill(3)] = normalized

        # =========================================================
        # 🔹 TIPO DECLARACIÓN
        # =========================================================
        declaration_type = "normal"
        lowered = full_text.lower()

        if "sin actividad" in lowered:
            declaration_type = "sin_actividad"
        elif "negativa" in lowered:
            declaration_type = "negativa"

        if "rectificativa" in lowered:
            declaration_type = "rectificativa"

        # =========================================================
        # 🔹 CAMPOS GENERALES
        # =========================================================
        nif_match = NIF_RE.search(full_text)
        period_match = PERIOD_RE.search(full_text)
        year_match = YEAR_RE.search(full_text)
        just_match = JUST_RE.search(full_text)
        prev_just_match = PREV_JUST_RE.search(full_text)

        return {
            "model_key": model_key,
            "nif": nif_match.group(1) if nif_match else None,
            "fiscal_year": year_match.group(1) if year_match else None,
            "period": period_match.group(1) if period_match else None,
            "reference_number": just_match.group(1) if just_match else None,
            "previous_reference": prev_just_match.group(1) if prev_just_match else None,
            "declaration_type": declaration_type,
            "boxes": boxes,
            "raw_text_excerpt": full_text[:2500],
        }
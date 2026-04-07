from __future__ import annotations

from src.models.contracts import Pdf303Data


class RectificativaService:
    def analyze(self, pdf_data: list[Pdf303Data | dict]) -> list[str]:
        messages: list[str] = []

        for idx, pdf in enumerate(pdf_data, start=1):

            # 🔥 SOPORTE MIXTO (objeto o dict)
            if isinstance(pdf, dict):
                declaration_type = pdf.get("declaration_type")
                previous_reference = pdf.get("previous_reference")
            else:
                declaration_type = getattr(pdf, "declaration_type", None)
                previous_reference = getattr(pdf, "previous_reference", None)

            # =========================
            # LÓGICA RECTIFICATIVA
            # =========================

            if declaration_type == "rectificativa":
                messages.append(
                    f"PDF {idx}: declaración rectificativa detectada. Justificante anterior: {previous_reference or 'no encontrado'}."
                )

                if not previous_reference:
                    messages.append(
                        f"PDF {idx}: falta el justificante anterior; revisar manualmente la regularización."
                    )

            elif declaration_type == "negativa":
                messages.append(f"PDF {idx}: declaración negativa detectada.")

            elif declaration_type == "sin_actividad":
                messages.append(f"PDF {idx}: declaración sin actividad detectada.")

        return messages
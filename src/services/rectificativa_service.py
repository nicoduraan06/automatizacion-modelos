from __future__ import annotations

from src.models.contracts import Pdf303Data


class RectificativaService:
    def analyze(self, pdf_data: list[Pdf303Data]) -> list[str]:
        messages: list[str] = []
        for idx, pdf in enumerate(pdf_data, start=1):
            if pdf.declaration_type == "rectificativa":
                messages.append(
                    f"PDF {idx}: declaración rectificativa detectada. Justificante anterior: {pdf.previous_reference or 'no encontrado'}."
                )
                if not pdf.previous_reference:
                    messages.append(
                        f"PDF {idx}: falta el justificante anterior; revisar manualmente la regularización."
                    )
        return messages

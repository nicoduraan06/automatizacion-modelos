from __future__ import annotations

import json

from src.models.contracts import ProcessManifest, ProcessResult
from src.parsers.excel_parser import ExcelParser
from src.parsers.pdf_parser import Pdf303Parser
from src.services.mapping_service import MappingService
from src.services.rectificativa_service import RectificativaService
from src.services.export_service import ExportService
from src.services.iva_detector import IVADetector  # 🔥 NUEVO
from src.storage.factory import get_storage
from src.utils.common import json_dumps


class ProcessService:
    def __init__(self):
        self.storage = get_storage()
        self.excel_parser = ExcelParser()
        self.pdf_parser = Pdf303Parser()
        self.mapping_service = MappingService()
        self.rectificativa_service = RectificativaService()
        self.export_service = ExportService()
        self.iva_detector = IVADetector()  # 🔥 NUEVO

    def _manifest_key(self, process_id: str) -> str:
        return f"{process_id}/manifest.json"

    def _result_key(self, process_id: str) -> str:
        return f"{process_id}/result.json"

    def _excel_key(self, process_id: str) -> str:
        return f"{process_id}/result.xlsx"

    def load_manifest(self, process_id: str) -> ProcessManifest:
        raw = self.storage.read_bytes(self._manifest_key(process_id))
        return ProcessManifest.model_validate_json(raw)

    def save_manifest(self, manifest: ProcessManifest) -> None:
        self.storage.write_bytes(
            self._manifest_key(manifest.process_id),
            manifest.model_dump_json(indent=2).encode("utf-8"),
            "application/json"
        )

    def save_result(self, result: ProcessResult) -> None:
        self.storage.write_bytes(
            self._result_key(result.process_id),
            result.model_dump_json(indent=2).encode("utf-8"),
            "application/json"
        )

    def save_excel(self, process_id: str, excel_bytes: bytes):
        self.storage.write_bytes(
            self._excel_key(process_id),
            excel_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def load_result(self, process_id: str) -> ProcessResult:
        raw = self.storage.read_bytes(self._result_key(process_id))
        return ProcessResult.model_validate_json(raw)

    def process(self, process_id: str) -> ProcessResult:
        manifest = self.load_manifest(process_id)

        manifest.status = "processing"
        self.save_manifest(manifest)

        # =========================
        # EXCEL
        # =========================
        excel_bytes = self.storage.read_bytes(manifest.excel.storage_key)

        excel_data = self.excel_parser.parse_bytes(
            filename=manifest.excel.name,
            content=excel_bytes
        )

        # =========================
        # PDF
        # =========================
        pdf_data = []

        for pdf in manifest.pdfs:
            pdf_bytes = self.storage.read_bytes(pdf.storage_key)
            parsed_pdf = self.pdf_parser.parse_bytes(pdf_bytes)
            pdf_data.append(parsed_pdf)

        reference_pdf = pdf_data[0] if pdf_data else None

        # =========================
        # 🔥 NUEVO: DETECTOR IVA
        # =========================
        iva_devengado = self.iva_detector.detect_devengado(excel_data)

        # =========================
        # MAPPING (actual)
        # =========================
        box_results = self.mapping_service.compute(excel_data, reference_pdf)

        # =========================
        # RECTIFICATIVA
        # =========================
        warnings = self.rectificativa_service.analyze(pdf_data)

        # =========================
        # VALIDACIÓN
        # =========================
        validations = self._validate(excel_data, pdf_data, box_results)

        result = ProcessResult(
            process_id=process_id,
            manifest=manifest,
            excel_data=excel_data,
            pdf_data=pdf_data,
            box_results=box_results,
            validations=validations,
            warnings=warnings,

            # 🔥 NUEVO OUTPUT ÚTIL
            extra_data={
                "iva_devengado": iva_devengado
            },

            summary={
                "boxes_total": len(box_results),
                "mismatches": sum(1 for x in box_results if x.status == "mismatch"),
                "warnings": len(warnings),
                "sheets_used": excel_data.sheets_used,
            },
        )

        # =========================
        # GUARDAR RESULTADOS
        # =========================
        self.save_result(result)

        # =========================
        # EXPORTAR EXCEL
        # =========================
        excel_output = self.export_service.to_excel_bytes(result)
        self.save_excel(process_id, excel_output)

        # =========================
        # FINALIZAR
        # =========================
        manifest.status = "processed"
        self.save_manifest(manifest)

        return result

    def _validate(self, excel_data, pdf_data, box_results):
        checks: list[str] = []

        if pdf_data:
            pdf0 = pdf_data[0]

            if isinstance(pdf0, dict):
                nif = pdf0.get("nif")
                period = pdf0.get("period")
                fiscal_year = pdf0.get("fiscal_year")
            else:
                nif = getattr(pdf0, "nif", None)
                period = getattr(pdf0, "period", None)
                fiscal_year = getattr(pdf0, "fiscal_year", None)

            if nif:
                checks.append(f"NIF PDF detectado: {nif}")

            if period and fiscal_year:
                checks.append(f"Periodo/Ejercicio PDF detectados: {period}/{fiscal_year}")

        mismatches = [x.box_code for x in box_results if x.status == "mismatch"]

        if mismatches:
            checks.append(f"Casillas con diferencias: {', '.join(mismatches)}")
        else:
            checks.append("No se detectan diferencias frente al PDF.")

        if not excel_data.sheets_used:
            checks.append("No se han detectado hojas relevantes en el Excel.")

        return checks
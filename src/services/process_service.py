from __future__ import annotations

import json

from src.models.contracts import ProcessManifest, ProcessResult
from src.parsers.excel_parser import ExcelParser
from src.parsers.pdf_parser import Pdf303Parser
from src.services.mapping_service import MappingService
from src.services.rectificativa_service import RectificativaService
from src.services.export_service import ExportService  # 🔥 NUEVO
from src.storage.factory import get_storage
from src.utils.common import json_dumps


class ProcessService:
    def __init__(self):
        self.storage = get_storage()
        self.excel_parser = ExcelParser()
        self.pdf_parser = Pdf303Parser()
        self.mapping_service = MappingService()
        self.rectificativa_service = RectificativaService()
        self.export_service = ExportService()  # 🔥 NUEVO

    def _manifest_key(self, process_id: str) -> str:
        return f"{process_id}/manifest.json"

    def _result_key(self, process_id: str) -> str:
        return f"{process_id}/result.json"

    def _excel_key(self, process_id: str) -> str:  # 🔥 NUEVO
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

    def save_excel(self, process_id: str, excel_bytes: bytes):  # 🔥 NUEVO
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

        # 🔹 Excel
        excel_bytes = self.storage.read_bytes(manifest.excel.storage_key)
        excel_data = self.excel_parser.parse(manifest.excel.name, excel_bytes)

        # 🔹 PDFs
        pdf_data = []
        for pdf in manifest.pdfs:
            pdf_bytes = self.storage.read_bytes(pdf.storage_key)
            pdf_data.append(self.pdf_parser.parse(pdf_bytes))

        reference_pdf = pdf_data[0] if pdf_data else None

        # 🔹 Mapping
        box_results = self.mapping_service.compute(excel_data, reference_pdf)

        # 🔹 Rectificativa
        warnings = self.rectificativa_service.analyze(pdf_data)

        # 🔹 Validación
        validations = self._validate(excel_data, pdf_data, box_results)

        result = ProcessResult(
            process_id=process_id,
            manifest=manifest,
            excel_data=excel_data,
            pdf_data=pdf_data,
            box_results=box_results,
            validations=validations,
            warnings=warnings,
            summary={
                "boxes_total": len(box_results),
                "mismatches": sum(1 for x in box_results if x.status == "mismatch"),
                "warnings": len(warnings),
                "sheets_used": excel_data.sheets_used,
            },
        )

        # 🔥 GUARDAR JSON
        self.save_result(result)

        # 🔥 GENERAR Y GUARDAR EXCEL
        excel_output = self.export_service.to_excel_bytes(result)
        self.save_excel(process_id, excel_output)

        # 🔹 Finalizar
        manifest.status = "processed"
        self.save_manifest(manifest)

        return result

    def _validate(self, excel_data, pdf_data, box_results):
        checks: list[str] = []

        if pdf_data:
            pdf0 = pdf_data[0]
            if pdf0.nif:
                checks.append(f"NIF PDF detectado: {pdf0.nif}")
            if pdf0.period and pdf0.fiscal_year:
                checks.append(f"Periodo/Ejercicio PDF detectados: {pdf0.period}/{pdf0.fiscal_year}")

        mismatches = [x.box_code for x in box_results if x.status == "mismatch"]

        if mismatches:
            checks.append(f"Casillas con diferencias: {', '.join(mismatches)}")
        else:
            checks.append("No se detectan diferencias frente al PDF.")

        if not excel_data.sheets_used:
            checks.append("No se han detectado hojas relevantes en el Excel.")

        return checks
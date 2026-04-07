from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class UploadedFileRef(BaseModel):
    name: str
    storage_key: str
    content_type: str | None = None
    size_bytes: int | None = None


class ProcessManifest(BaseModel):
    process_id: str
    created_at: str
    status: Literal["uploaded", "processing", "processed", "error"] = "uploaded"
    excel: UploadedFileRef
    pdfs: list[UploadedFileRef] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)


class TraceCell(BaseModel):
    sheet: str
    cell: str
    value: Any = None
    formula: str | None = None
    label: str | None = None


class BoxResult(BaseModel):
    box_code: str
    description: str | None = None
    excel_value: float | int | None = None
    pdf_value: float | int | None = None
    difference: float | None = None
    status: Literal["ok", "warning", "mismatch", "missing"]
    rule_name: str
    evidence: list[TraceCell] = Field(default_factory=list)


class Pdf303Data(BaseModel):
    nif: str | None = None
    company_name: str | None = None
    fiscal_year: str | None = None
    period: str | None = None
    reference_number: str | None = None
    declaration_type: str | None = None
    previous_reference: str | None = None
    boxes: dict[str, float] = Field(default_factory=dict)
    raw_text_excerpt: str | None = None


class Excel303Data(BaseModel):
    workbook_name: str
    sheets_used: list[str] = Field(default_factory=list)
    cell_index: dict[str, dict[str, Any]] = Field(default_factory=dict)
    label_index: dict[str, list[TraceCell]] = Field(default_factory=dict)


class ProcessResult(BaseModel):
    process_id: str
    manifest: ProcessManifest
    excel_data: Excel303Data
    pdf_data: list[Pdf303Data]
    box_results: list[BoxResult]
    validations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)

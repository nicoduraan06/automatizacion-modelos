from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RuleType = Literal[
    "direct_cell",
    "sum_cells",
    "label_match",
    "fixed_value",
    "formula"
]


class FieldSourceHint(BaseModel):
    source_type: Literal["excel_label", "excel_sheet", "pdf_text", "pdf_regex"]
    value: str


class FieldRule(BaseModel):
    rule_type: RuleType
    config: dict[str, Any] = Field(default_factory=dict)


class ModelFieldDefinition(BaseModel):
    key: str
    label: str
    target_type: Literal["number", "string", "boolean"] = "number"
    required: bool = False
    source_hints: list[FieldSourceHint] = Field(default_factory=list)
    rules: list[FieldRule] = Field(default_factory=list)
    description: Optional[str] = None


class ModelValidationRule(BaseModel):
    key: str
    rule_type: Literal["sum_equals", "required_if_present", "same_value", "custom"]
    config: dict[str, Any] = Field(default_factory=dict)
    message: str


class ModelDefinition(BaseModel):
    model_key: str
    name: str
    version: str = "1.0"
    aliases: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    excel_sheet_hints: list[str] = Field(default_factory=list)
    pdf_text_hints: list[str] = Field(default_factory=list)
    fields: list[ModelFieldDefinition] = Field(default_factory=list)
    validations: list[ModelValidationRule] = Field(default_factory=list)
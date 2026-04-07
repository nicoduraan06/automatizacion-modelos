from __future__ import annotations

import json
from pathlib import Path

from src.models.model_definition import ModelDefinition


class ModelRegistry:
    def __init__(self, base_path: str = "src/mappings"):
        self.base_path = Path(base_path)

    def get_definition(self, model_key: str) -> ModelDefinition:
        file_path = self.base_path / f"{model_key}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"No existe definición para el modelo '{model_key}'")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ModelDefinition.model_validate(data)

    def list_available_models(self) -> list[str]:
        if not self.base_path.exists():
            return []

        return sorted([p.stem for p in self.base_path.glob("*.json")])
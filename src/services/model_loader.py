import json
import os


class ModelLoader:

    BASE_PATH = "src/mappings"

    def load(self, model_key: str):
        file_path = os.path.join(self.BASE_PATH, f"{model_key}_rules.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No existe configuración para modelo: {model_key}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
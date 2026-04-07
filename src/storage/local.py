from __future__ import annotations

from pathlib import Path

from src.config import settings
from src.storage.base import StorageBackend
from src.utils.common import ensure_parent


class LocalStorage(StorageBackend):
    def __init__(self, root: str | None = None):
        self.root = Path(root or settings.local_storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def write_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        path = self._path(key)
        ensure_parent(path)
        path.write_bytes(data)

    def read_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def public_or_signed_url(self, key: str) -> str | None:
        return None

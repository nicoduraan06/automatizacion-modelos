from __future__ import annotations

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def write_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def public_or_signed_url(self, key: str) -> str | None:
        raise NotImplementedError

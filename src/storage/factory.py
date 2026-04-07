from src.config import settings
from src.storage.local import LocalStorage
from src.storage.s3 import S3Storage


def get_storage():
    if settings.storage_backend.lower() == "s3":
        return S3Storage()
    return LocalStorage()

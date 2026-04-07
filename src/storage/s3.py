from __future__ import annotations

import boto3

from src.config import settings
from src.storage.base import StorageBackend


class S3Storage(StorageBackend):
    def __init__(self):
        self.bucket = settings.s3_bucket
        if not self.bucket:
            raise ValueError("S3_BUCKET es obligatorio cuando STORAGE_BACKEND=s3")
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_default_region,
        )

    def write_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)

    def read_bytes(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def public_or_signed_url(self, key: str) -> str | None:
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )

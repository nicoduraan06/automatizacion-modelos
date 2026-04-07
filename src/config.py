from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    storage_backend: str = "local"
    local_storage_root: str = "/tmp/modelo303_storage"
    result_ttl_hours: int = 24
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_default_region: str = "eu-west-1"
    s3_bucket: str | None = None
    s3_prefix: str = "modelo303"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

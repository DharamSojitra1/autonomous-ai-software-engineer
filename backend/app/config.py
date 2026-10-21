
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "AI Software Engineer"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    workspace_root: Path = (
        Path(__file__).resolve().parents[2] / "data" / "workspaces"
    )
    max_upload_size_mb: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    max_upload_size_mb: int = 50
    max_archive_files: int = 2_000
    max_extracted_size_mb: int = 200
    max_read_file_size_kb: int = 512
    max_search_results: int = 100
    max_search_file_size_kb: int = 512


@lru_cache
def get_settings() -> Settings:
    return Settings()

import typing
from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings

from src.core.settings.cors import CORSSettings
from src.core.settings.uvicorn import UvicornSettings


class RunMode(str, Enum):
    dev = "DEV"
    prod = "PRODUCTION"


class Settings(BaseSettings):
    """Deposit Service API settings."""

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    api_prefix: str = ""
    root_path: str = ""
    app_version: str = "latest"
    project_name: str
    app_slug: str
    secret_jwt: str
    logging_level: str

    # application run mod: DEV/PRODUCTION
    run_mode: typing.Optional[RunMode] = RunMode.prod

    debug: typing.Optional[bool]

    uvicorn: UvicornSettings
    cors: CORSSettings = CORSSettings()


@lru_cache
def get_settings() -> Settings:
    """Получение и кэширование настроек проекта."""
    _settings = Settings()
    return _settings


settings = get_settings()

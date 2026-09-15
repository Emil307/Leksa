"""Конфигурация приложения."""

from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

import pytz
from pydantic import Field
from pydantic_settings import BaseSettings


def normalize_url(url: str) -> str:
    """Нормализовать URL, экранируя специальные символы в пароле."""
    try:
        scheme_end = url.find("://")
        if scheme_end == -1:
            return url

        auth_start = scheme_end + 3
        last_at = url.rfind("@")
        if last_at == -1:
            return url

        scheme = url[:scheme_end + 3]
        auth_part = url[auth_start:last_at]
        rest = url[last_at + 1:]

        if ":" not in auth_part:
            return url

        user, password = auth_part.split(":", 1)
        encoded_password = quote(password, safe="")

        return f"{scheme}{user}:{encoded_password}@{rest}"

    except Exception:
        return url


class AppSettings(BaseSettings):
    """Конфигурация приложения."""

    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    name: str = Field(default="Uwords Bot API", env="NAME")
    description: str = Field(default="API for Uwords Bot", env="DESCRIPTION")
    version: str = Field(default="1.0.0", env="VERSION")

    class Config:
        env_prefix = "APP_"


class BotSettings(BaseSettings):
    """Конфигурация Telegram."""

    token: str = Field(env="TOKEN")
    link: str = Field(default="", env="LINK")
    admin_chat_id: int = Field(default=0, env="ADMIN_CHAT_ID")
    secret_token: str = Field(default="", env="SECRET_TOKEN")
    webhook_url: str = Field(default="", env="WEBHOOK_URL")

    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    name: str = Field(default="Uwords Bot", env="NAME")

    class Config:
        env_prefix = "BOT_"


class CORSSettings(BaseSettings):
    """Конфигурация CORS."""

    origins: List[str] = Field(default=["*"], env="ORIGINS")
    allow_credentials: bool = Field(default=True, env="ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default=["*"], env="ALLOW_METHODS")
    allow_headers: List[str] = Field(default=["*"], env="ALLOW_HEADERS")

    class Config:
        env_prefix = "CORS_"


class DatabaseSettings(BaseSettings):
    """Конфигурация базы данных."""

    name: str = Field(default="uwords", env="NAME")
    user: str = Field(default="postgres", env="USER")
    password: str = Field(default="postgres", env="PASSWORD")
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=5432, env="PORT")

    @property
    def url(self) -> str:
        url = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return normalize_url(url)

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Конфигурация Redis."""

    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=6379, env="PORT")
    password: Optional[str] = Field(default=None, env="PASSWORD")
    db: int = Field(default=0, env="DB")
    decode_responses: bool = Field(default=True, env="DECODE_RESPONSES")

    @property
    def url(self) -> str:
        if self.password:
            url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            url = f"redis://{self.host}:{self.port}/{self.db}"
        return normalize_url(url)

    class Config:
        env_prefix = "REDIS_"


class Settings(BaseSettings):
    """Главный класс настроек приложения."""

    debug: bool = Field(default=False, env="DEBUG")
    timezone_str: str = Field(default="Europe/Moscow", env="TIMEZONE_STR")

    base_dir: Path = Path(__file__).parent.parent

    app: AppSettings = Field(default_factory=AppSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    @property
    def timezone(self) -> pytz.timezone:
        return pytz.timezone(self.timezone_str)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Получить синглтон настроек."""
    global settings

    if settings is None:
        settings = Settings()

    return settings

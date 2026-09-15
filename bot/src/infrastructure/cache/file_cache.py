"""Кэш file_id для Telegram файлов (фото, видео, документы)."""

from typing import Optional

from core.logger import setup_logger

from infrastructure.cache.redis_client import RedisClient
from infrastructure.cache.factory import create_redis_client


logger = setup_logger("FILE CACHE")


class FileCache:
    """Кэш file_id в Redis."""

    def __init__(self):
        self._client: Optional[RedisClient] = None

    @property
    def client(self) -> RedisClient:
        if self._client is None:
            self._client = create_redis_client()
        return self._client

    async def get_file_id(self, key: str) -> Optional[str]:
        """Получить file_id из кэша."""
        return await self.client.get(f"file_cache:{key}")

    async def set_file_id(self, key: str, file_id: str) -> bool:
        """Сохранить file_id в кэш."""
        return await self.client.set(f"file_cache:{key}", file_id)


_file_cache: Optional[FileCache] = None


def get_file_cache() -> FileCache:
    """Получить синглтон FileCache."""
    global _file_cache
    if _file_cache is None:
        _file_cache = FileCache()
    return _file_cache

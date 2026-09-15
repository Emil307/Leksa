"""Фабрика для создания Redis клиента."""

from typing import Optional

from core.config import get_settings
from core.logger import setup_logger

from infrastructure.cache.redis_client import RedisClient

logger = setup_logger("REDIS FACTORY", "DEBUG")

_redis_client_instance: Optional[RedisClient] = None


def create_redis_client() -> RedisClient:
    """Создать или получить синглтон Redis клиента."""
    global _redis_client_instance

    if _redis_client_instance is None:
        settings = get_settings()

        _redis_client_instance = RedisClient(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password if settings.redis.password else None,
            db=settings.redis.db,
            decode_responses=settings.redis.decode_responses,
        )

        logger.info("Redis client instance created")

    return _redis_client_instance


def get_redis_client() -> Optional[RedisClient]:
    """Получить текущий экземпляр Redis клиента."""
    return _redis_client_instance

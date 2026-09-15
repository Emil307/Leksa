"""Redis клиент для работы с кэшем."""

from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from core.logger import setup_logger

from domain.exceptions import ErrorCode, InternalServerErrorException

logger = setup_logger("REDIS CLIENT", "DEBUG")


class RedisClient:
    """Клиент для работы с Redis."""

    def __init__(
        self,
        host: str,
        port: int,
        password: Optional[str] = None,
        db: int = 0,
        decode_responses: bool = True,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.decode_responses = decode_responses
        self._client: Optional[Redis] = None

    async def connect(self) -> None:
        """Подключиться к Redis."""
        if self._client is None:
            if self.password:
                url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            else:
                url = f"redis://{self.host}:{self.port}/{self.db}"

            self._client = await redis.from_url(url, decode_responses=self.decode_responses)
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

    async def disconnect(self) -> None:
        """Отключиться от Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу."""
        if self._client is None:
            await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Установить значение по ключу."""
        if self._client is None:
            await self.connect()
        if ttl is not None:
            return await self._client.setex(key, ttl, value)
        else:
            return await self._client.set(key, value)

    async def delete(self, key: str) -> int:
        """Удалить ключ."""
        if self._client is None:
            await self.connect()
        return await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        """Проверить существование ключа."""
        if self._client is None:
            await self.connect()
        return await self._client.exists(key) > 0

    @property
    def client(self) -> Redis:
        """Получить нативный клиент Redis."""
        if self._client is None:
            raise InternalServerErrorException(
                "Redis client is not connected. Call connect() first.",
                code=ErrorCode.internal,
            )
        return self._client

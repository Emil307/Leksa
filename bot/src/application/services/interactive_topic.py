"""Сервис интерактивных тем."""

from typing import List, Tuple

from core.logger import setup_logger

from domain.entities.interactive_topic import InteractiveTopic
from infrastructure.repositories.factory import get_interactive_topic_repository


class InteractiveTopicService:
    """Сервис для работы с интерактивными темами."""

    def __init__(self):
        self.logger = setup_logger("INTERACTIVE TOPIC SERVICE")
        self.repo = get_interactive_topic_repository()

    async def get_all(
        self,
        page: int = 0,
        per_page: int = 5,
    ) -> Tuple[List[InteractiveTopic], int]:
        """Получить все активные темы с пагинацией."""
        return await self.repo.get_all_active(limit=per_page, offset=page * per_page)

    async def get_by_level(
        self,
        level: str,
        page: int = 0,
        per_page: int = 5,
    ) -> Tuple[List[InteractiveTopic], int]:
        """Получить темы по уровню с пагинацией."""
        return await self.repo.get_by_level(level, limit=per_page, offset=page * per_page)


_service: InteractiveTopicService = None


def get_interactive_topic_service() -> InteractiveTopicService:
    """Получить синглтон сервиса интерактивных тем."""
    global _service
    if _service is None:
        _service = InteractiveTopicService()
    return _service

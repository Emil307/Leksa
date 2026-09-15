"""Сервис учебных материалов."""

from typing import List, Tuple

from core.logger import setup_logger

from domain.entities.educational_topic import EducationalTopic
from infrastructure.repositories.factory import get_educational_topic_repository


class EducationalTopicService:
    """Сервис для работы с учебными темами."""

    def __init__(self):
        self.logger = setup_logger("EDUCATIONAL TOPIC SERVICE")
        self.repo = get_educational_topic_repository()

    async def get_by_level(
        self,
        level: str,
        page: int = 0,
        per_page: int = 5,
    ) -> Tuple[List[EducationalTopic], int]:
        """Получить темы по уровню с пагинацией."""
        return await self.repo.get_by_level(level, limit=per_page, offset=page * per_page)


_service: EducationalTopicService = None


def get_educational_topic_service() -> EducationalTopicService:
    """Получить синглтон сервиса учебных тем."""
    global _service
    if _service is None:
        _service = EducationalTopicService()
    return _service

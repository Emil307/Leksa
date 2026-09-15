"""Сервис идиом."""

from typing import List

from core.logger import setup_logger

from domain.entities.idiom import Idiom
from infrastructure.repositories.factory import get_idiom_repository


class IdiomService:
    """Сервис для работы с идиомами."""

    def __init__(self):
        self.logger = setup_logger("IDIOM SERVICE")
        self.repo = get_idiom_repository()

    async def get_random_idioms(self, count: int = 10) -> List[Idiom]:
        """Получить случайные идиомы."""
        return await self.repo.get_random(limit=count)


_service: IdiomService = None


def get_idiom_service() -> IdiomService:
    """Получить синглтон сервиса идиом."""
    global _service
    if _service is None:
        _service = IdiomService()
    return _service

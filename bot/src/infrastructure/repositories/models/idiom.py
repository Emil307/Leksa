"""Репозиторий идиом."""

from typing import List

from sqlalchemy import func

from domain.entities.idiom import Idiom
from infrastructure.database.models.idiom import IdiomModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.idiom import get_idiom_mapper


class IdiomRepository(SQLAlchemyRepository):
    """Репозиторий для работы с идиомами."""

    model = IdiomModel

    def __init__(self):
        super().__init__()
        self.mapper = get_idiom_mapper()

    async def get_random(self, limit: int = 10) -> List[Idiom]:
        """Получить случайные идиомы."""
        items = await self.get_all_by_filter(
            filters=[IdiomModel.is_active == True],
            order=[func.random()],
            limit=limit,
        )
        return [self.mapper.to_domain(i) for i in items]

    async def get_all_active(self) -> List[Idiom]:
        """Получить все активные идиомы."""
        items = await self.get_all_by_filter(
            filters=[IdiomModel.is_active == True],
        )
        return [self.mapper.to_domain(i) for i in items]

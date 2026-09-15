"""Репозиторий интерактивных тем."""

from typing import List, Tuple

from domain.entities.interactive_topic import InteractiveTopic
from infrastructure.database.models.interactive_topic import InteractiveTopicModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.interactive_topic import get_interactive_topic_mapper


class InteractiveTopicRepository(SQLAlchemyRepository):
    """Репозиторий для работы с интерактивными темами."""

    model = InteractiveTopicModel

    def __init__(self):
        super().__init__()
        self.mapper = get_interactive_topic_mapper()

    async def get_all_active(
        self,
        limit: int = 5,
        offset: int = 0,
    ) -> Tuple[List[InteractiveTopic], int]:
        """Получить все активные темы с пагинацией."""
        items, total = await self.get_paginated_by_filter(
            filters=[InteractiveTopicModel.is_active == True],
            order=[InteractiveTopicModel.order.asc()],
            limit=limit,
            offset=offset,
        )
        return [self.mapper.to_domain(i) for i in items], total

    async def get_by_level(
        self,
        level: str,
        limit: int = 5,
        offset: int = 0,
    ) -> Tuple[List[InteractiveTopic], int]:
        """Получить темы по уровню с пагинацией."""
        items, total = await self.get_paginated_by_filter(
            filters=[InteractiveTopicModel.level == level, InteractiveTopicModel.is_active == True],
            order=[InteractiveTopicModel.order.asc()],
            limit=limit,
            offset=offset,
        )
        return [self.mapper.to_domain(i) for i in items], total

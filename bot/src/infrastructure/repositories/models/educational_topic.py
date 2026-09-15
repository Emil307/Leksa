"""Репозиторий учебных материалов."""

from typing import List, Tuple

from domain.entities.educational_topic import EducationalTopic
from infrastructure.database.models.educational_topic import EducationalTopicModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.educational_topic import get_educational_topic_mapper


class EducationalTopicRepository(SQLAlchemyRepository):
    """Репозиторий для работы с учебными темами."""

    model = EducationalTopicModel

    def __init__(self):
        super().__init__()
        self.mapper = get_educational_topic_mapper()

    async def get_by_level(
        self,
        level: str,
        limit: int = 5,
        offset: int = 0,
    ) -> Tuple[List[EducationalTopic], int]:
        """Получить темы по уровню с пагинацией."""
        items, total = await self.get_paginated_by_filter(
            filters=[EducationalTopicModel.level == level, EducationalTopicModel.is_active == True],
            order=[EducationalTopicModel.order.asc()],
            limit=limit,
            offset=offset,
        )
        return [self.mapper.to_domain(i) for i in items], total

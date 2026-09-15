"""Репозитории FAQ."""

from typing import List, Optional

from domain.entities.faq import FAQCategory, FAQItem
from infrastructure.database.models.faq_category import FAQCategoryModel
from infrastructure.database.models.faq_item import FAQItemModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.faq import get_faq_category_mapper, get_faq_item_mapper


class FAQCategoryRepository(SQLAlchemyRepository):
    """Репозиторий для работы с категориями FAQ."""

    model = FAQCategoryModel

    def __init__(self):
        super().__init__()
        self.mapper = get_faq_category_mapper()

    async def get_all_active(self) -> List[FAQCategory]:
        """Получить все активные категории."""
        items = await self.get_all_by_filter(
            filters=[FAQCategoryModel.is_active == True],
            order=[FAQCategoryModel.order.asc()],
        )
        return [self.mapper.to_domain(i) for i in items]


class FAQItemRepository(SQLAlchemyRepository):
    """Репозиторий для работы с элементами FAQ."""

    model = FAQItemModel

    def __init__(self):
        super().__init__()
        self.mapper = get_faq_item_mapper()

    async def get_by_category(self, category_id: int) -> List[FAQItem]:
        """Получить элементы FAQ по категории."""
        items = await self.get_all_by_filter(
            filters=[FAQItemModel.category_id == category_id, FAQItemModel.is_active == True],
            order=[FAQItemModel.order.asc()],
        )
        return [self.mapper.to_domain(i) for i in items]

    async def get_by_id(self, item_id: int) -> Optional[FAQItem]:
        """Получить элемент FAQ по ID."""
        item = await self.get_one(filters=[FAQItemModel.id == item_id])
        return self.mapper.to_domain(item) if item else None

    async def get_all_paginated(
        self,
        limit: int = 5,
        offset: int = 0,
    ) -> tuple[List[FAQItem], int]:
        """Получить все активные элементы FAQ с пагинацией."""
        items, total = await self.get_paginated_by_filter(
            filters=[FAQItemModel.is_active == True],
            order=[FAQItemModel.order.asc()],
            limit=limit,
            offset=offset,
        )
        return [self.mapper.to_domain(i) for i in items], total

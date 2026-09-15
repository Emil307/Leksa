"""Сервис FAQ."""

from typing import List, Optional, Tuple

from core.logger import setup_logger

from domain.entities.faq import FAQCategory, FAQItem
from infrastructure.repositories.factory import get_faq_category_repository, get_faq_item_repository


class FAQService:
    """Сервис для работы с FAQ."""

    def __init__(self):
        self.logger = setup_logger("FAQ SERVICE")
        self.category_repo = get_faq_category_repository()
        self.item_repo = get_faq_item_repository()

    async def get_categories(self) -> List[FAQCategory]:
        """Получить все активные категории."""
        return await self.category_repo.get_all_active()

    async def get_items_by_category(self, category_id: int) -> List[FAQItem]:
        """Получить элементы FAQ по категории."""
        return await self.item_repo.get_by_category(category_id)

    async def get_item(self, item_id: int) -> Optional[FAQItem]:
        """Получить элемент FAQ по ID."""
        return await self.item_repo.get_by_id(item_id)

    async def get_all_items_paginated(
        self,
        page: int = 0,
        per_page: int = 5,
    ) -> Tuple[List[FAQItem], int]:
        """Получить все активные элементы FAQ с пагинацией."""
        offset = page * per_page
        return await self.item_repo.get_all_paginated(
            limit=per_page,
            offset=offset,
        )


_service: FAQService = None


def get_faq_service() -> FAQService:
    """Получить синглтон сервиса FAQ."""
    global _service
    if _service is None:
        _service = FAQService()
    return _service

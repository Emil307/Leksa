"""Доменные сущности FAQ."""

from typing import Optional, List

from domain.entities._base import DomainEntity


class FAQItem(DomainEntity):
    """Элемент FAQ."""

    id: Optional[int] = None
    category_id: int
    question: str
    answer: str
    order: int = 0
    is_active: bool = True


class FAQCategory(DomainEntity):
    """Категория FAQ с вложенными элементами."""

    _relation_fields = {"items"}

    id: Optional[int] = None
    title: str
    emoji: str = "❓"
    order: int = 0
    is_active: bool = True
    items: List[FAQItem] = []

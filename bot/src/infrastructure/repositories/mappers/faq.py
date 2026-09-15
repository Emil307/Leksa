"""Мапперы FAQ."""

from domain.entities.faq import FAQCategory, FAQItem
from infrastructure.database.models.faq_category import FAQCategoryModel
from infrastructure.database.models.faq_item import FAQItemModel
from infrastructure.repositories.mappers._base import BaseMapper


class FAQCategoryMapper(BaseMapper[FAQCategory, FAQCategoryModel]):
    """Маппер FAQCategory <-> FAQCategoryModel."""

    domain_class = FAQCategory


class FAQItemMapper(BaseMapper[FAQItem, FAQItemModel]):
    """Маппер FAQItem <-> FAQItemModel."""

    domain_class = FAQItem


def get_faq_category_mapper() -> FAQCategoryMapper:
    """Получить экземпляр маппера категорий FAQ."""
    return FAQCategoryMapper()


def get_faq_item_mapper() -> FAQItemMapper:
    """Получить экземпляр маппера элементов FAQ."""
    return FAQItemMapper()

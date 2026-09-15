"""Доменная сущность учебных материалов."""

from typing import Optional

from domain.entities._base import DomainEntity
from domain.enums.topic import TopicLevel


class EducationalTopic(DomainEntity):
    """Учебная тема с привязкой к уровню."""

    id: Optional[int] = None
    title: str
    level: TopicLevel
    url: Optional[str] = None
    emoji: str = "📗"
    order: int = 0
    is_active: bool = True

    @property
    def button_text(self) -> str:
        return f"{self.title} {self.emoji}"

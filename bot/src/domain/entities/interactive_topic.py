"""Доменная сущность интерактивных тем."""

from typing import Optional

from domain.entities._base import DomainEntity
from domain.enums.topic import TopicLevel


class InteractiveTopic(DomainEntity):
    """Интерактивная тема для практики."""

    id: Optional[int] = None
    title: str
    level: Optional[TopicLevel] = None
    url: Optional[str] = None
    emoji: str = "🎯"
    order: int = 0
    is_active: bool = True

    @property
    def button_text(self) -> str:
        return f"{self.title} {self.emoji}"

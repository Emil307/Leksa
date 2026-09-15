"""Доменная сущность вопроса по грамматике."""

from typing import Optional, List

from domain.entities._base import DomainEntity


class GrammarQuestion(DomainEntity):
    """Вопрос по грамматике (fill-in-the-blank)."""

    id: Optional[int] = None
    phrase: str  # "I'm good ___ math"
    correct_answer: str  # "at"
    options: List[str] = []  # ["in", "at", "on", "to"]
    explanation: Optional[str] = None
    level: Optional[str] = None  # "beginner" | "intermediate" | "advanced"
    media_file: Optional[str] = None
    media_type: Optional[str] = None  # "photo" | "video"
    is_active: bool = True

    @property
    def correct_index(self) -> int:
        try:
            return self.options.index(self.correct_answer)
        except ValueError:
            return 0

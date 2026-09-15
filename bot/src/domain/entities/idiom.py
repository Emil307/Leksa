"""Доменная сущность идиомы."""

from typing import Optional, List

from domain.entities._base import DomainEntity


class Idiom(DomainEntity):
    """Идиома для теста."""

    id: Optional[int] = None
    phrase: str
    meaning: str
    example: Optional[str] = None
    options: List[str] = []
    correct_index: int = 0
    media_file: Optional[str] = None
    media_type: Optional[str] = None  # "photo" | "video"
    is_active: bool = True

    @property
    def correct_answer(self) -> str:
        if self.options and 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return ""

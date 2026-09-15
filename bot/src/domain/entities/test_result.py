"""Доменная сущность результатов тестов."""

from typing import Optional, Any

from domain.entities._base import DomainEntity
from domain.enums.test import TestType


class TestResult(DomainEntity):
    """Результат прохождения теста."""

    id: Optional[int] = None
    user_id: int
    test_type: TestType
    score: int = 0
    max_score: int = 0
    details: Optional[Any] = None

    @property
    def percentage(self) -> int:
        if self.max_score == 0:
            return 0
        return round(self.score / self.max_score * 100)

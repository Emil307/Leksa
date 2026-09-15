"""Сервис тестирования."""

from typing import List, Any, Optional

from core.logger import setup_logger

from domain.entities.test_result import TestResult
from infrastructure.repositories.factory import get_test_result_repository


class TestService:
    """Сервис для работы с тестами."""

    def __init__(self):
        self.logger = setup_logger("TEST SERVICE")
        self.repo = get_test_result_repository()

    async def save_result(
        self,
        user_id: int,
        test_type: str,
        score: int,
        max_score: int,
        details: Optional[Any] = None,
    ) -> TestResult:
        """Сохранить результат теста."""
        data = {
            "user_id": user_id,
            "test_type": test_type,
            "score": score,
            "max_score": max_score,
            "details": details,
        }
        result = await self.repo.create(data)
        return result

    async def get_results(self, user_id: int, test_type: str) -> List[TestResult]:
        """Получить результаты пользователя по типу теста."""
        return await self.repo.get_by_user_and_type(user_id, test_type)

    async def get_tests_count(self, user_id: int) -> int:
        """Подсчитать количество пройденных тестов."""
        return await self.repo.count_by_user(user_id)


_service: TestService = None


def get_test_service() -> TestService:
    """Получить синглтон сервиса тестирования."""
    global _service
    if _service is None:
        _service = TestService()
    return _service

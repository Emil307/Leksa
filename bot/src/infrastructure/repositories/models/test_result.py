"""Репозиторий результатов тестов."""

from typing import Optional, List

from domain.entities.test_result import TestResult
from infrastructure.database.models.test_result import TestResultModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.test_result import get_test_result_mapper


class TestResultRepository(SQLAlchemyRepository):
    """Репозиторий для работы с результатами тестов."""

    model = TestResultModel

    def __init__(self):
        super().__init__()
        self.mapper = get_test_result_mapper()

    async def create(self, data: dict) -> Optional[TestResult]:
        """Создать результат теста."""
        item = await self.add_one(data)
        return self.mapper.to_domain(item) if item else None

    async def get_by_user_and_type(self, user_id: int, test_type: str) -> List[TestResult]:
        """Получить результаты пользователя по типу теста."""
        items = await self.get_all_by_filter(
            filters=[TestResultModel.user_id == user_id, TestResultModel.test_type == test_type],
            order=[TestResultModel.created_at.desc()],
        )
        return [self.mapper.to_domain(i) for i in items]

    async def count_by_user(self, user_id: int) -> int:
        """Подсчитать количество тестов пользователя."""
        return await self.count_by_filter(filters=[TestResultModel.user_id == user_id])

"""Маппер результатов тестов."""

from domain.entities.test_result import TestResult
from infrastructure.database.models.test_result import TestResultModel
from infrastructure.repositories.mappers._base import BaseMapper


class TestResultMapper(BaseMapper[TestResult, TestResultModel]):
    """Маппер TestResult <-> TestResultModel."""

    domain_class = TestResult


def get_test_result_mapper() -> TestResultMapper:
    """Получить экземпляр маппера результатов тестов."""
    return TestResultMapper()

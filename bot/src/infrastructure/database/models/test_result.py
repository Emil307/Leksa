"""ORM модель результатов тестов."""

from sqlalchemy import Enum as SAEnum, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums.test import TestType
from infrastructure.database.base import Base, TimestampMixin


class TestResultModel(Base, TimestampMixin):
    """Таблица test_results."""

    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_type: Mapped[TestType] = mapped_column(SAEnum(TestType), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[str] = mapped_column(JSON, nullable=True)

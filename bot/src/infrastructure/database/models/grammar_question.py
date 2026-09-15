"""ORM модель вопроса по грамматике."""

from sqlalchemy import Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base, TimestampMixin


class GrammarQuestionModel(Base, TimestampMixin):
    """Таблица grammar_questions."""

    __tablename__ = "grammar_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phrase: Mapped[str] = mapped_column(String(500), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(100), nullable=False)
    options: Mapped[str] = mapped_column(JSON, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=True)
    media_file: Mapped[str] = mapped_column(String(255), nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

"""ORM модель учебных материалов."""

from sqlalchemy import Enum as SAEnum, Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums.topic import TopicLevel
from infrastructure.database.base import Base, TimestampMixin


class EducationalTopicModel(Base, TimestampMixin):
    """Таблица educational_topics."""

    __tablename__ = "educational_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[TopicLevel] = mapped_column(SAEnum(TopicLevel), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=True)
    emoji: Mapped[str] = mapped_column(String(10), default="📗")
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

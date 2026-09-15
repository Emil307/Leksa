"""ORM модель игровой сессии."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum as SAEnum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums.game import GameSessionStatus
from infrastructure.database.base import Base, TimestampMixin


class GameSessionModel(Base, TimestampMixin):
    """Таблица game_sessions."""

    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[GameSessionStatus] = mapped_column(SAEnum(GameSessionStatus), default=GameSessionStatus.in_progress, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

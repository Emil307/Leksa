"""ORM модель топиков игр пользователей."""

from sqlalchemy import Integer, BigInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base, TimestampMixin


class UserGameThreadModel(Base, TimestampMixin):
    """Таблица user_game_threads."""

    __tablename__ = "user_game_threads"
    __table_args__ = (
        UniqueConstraint("user_id", "game_type", name="uq_user_game_thread"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    game_type: Mapped[str] = mapped_column(String(30), nullable=False)
    thread_id: Mapped[int] = mapped_column(Integer, nullable=False)

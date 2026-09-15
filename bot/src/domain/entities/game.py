"""Доменные сущности игр."""

from typing import Optional
from datetime import datetime

from domain.entities._base import DomainEntity
from domain.enums.game import GameSessionStatus


class Game(DomainEntity):
    """Игра."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    emoji: str = "🎮"
    is_premium: bool = False
    is_active: bool = True
    order: int = 0

    @property
    def button_text(self) -> str:
        return f"{self.emoji} {self.name}"


class GameSession(DomainEntity):
    """Игровая сессия пользователя."""

    id: Optional[int] = None
    user_id: int
    game_id: int
    score: int = 0
    status: GameSessionStatus = GameSessionStatus.in_progress
    completed_at: Optional[datetime] = None

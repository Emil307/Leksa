"""Доменная сущность топика игры пользователя."""

from typing import Optional
from datetime import datetime

from domain.entities._base import DomainEntity


class UserGameThread(DomainEntity):
    """Топик игры пользователя в приватном чате."""

    id: Optional[int] = None
    user_id: int
    game_type: str  # "idioms" | "grammar" | "cards"
    thread_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

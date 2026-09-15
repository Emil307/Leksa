"""Доменная сущность пользователя."""

from typing import Optional

from pydantic import BaseModel

from domain.entities._base import DomainEntity


class User(DomainEntity):
    """Пользователь Telegram-бота."""

    id: Optional[int] = None
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_active: bool = True

    @property
    def display_name(self) -> str:
        if self.first_name:
            return self.first_name
        if self.username:
            return f"@{self.username}"
        return str(self.telegram_id)


class UserCreate(BaseModel):
    """Данные для создания пользователя."""

    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class UserUpdate(BaseModel):
    """Данные для обновления пользователя."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

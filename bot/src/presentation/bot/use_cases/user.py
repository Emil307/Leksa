"""
Use case пользователя для бота.
"""
from typing import Optional

from application.services.user import UserService, get_user_service

from domain.entities.user import User


class UserUseCase:
    """Use case для работы с пользователем."""

    def __init__(self) -> None:
        self.user_service: UserService = get_user_service()

    async def get_or_create_user(
        self,
        telegram_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> User:
        """Получить или создать пользователя."""
        return await self.user_service.get_or_create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code,
        )


_user_use_case: Optional[UserUseCase] = None


def get_user_use_case() -> UserUseCase:
    """Получить синглтон UserUseCase."""
    global _user_use_case
    if _user_use_case is None:
        _user_use_case = UserUseCase()
    return _user_use_case

"""Сервис пользователя."""

from typing import Optional

from core.logger import setup_logger

from domain.entities.user import User, UserCreate, UserUpdate
from infrastructure.repositories.factory import get_user_repository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self):
        self.logger = setup_logger("USER SERVICE", "DEBUG")
        self.user_repository = get_user_repository()

    async def get_or_create_user(
        self,
        telegram_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> User:
        """Получить или создать пользователя."""
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if user is not None:
            update_data = UserUpdate(
                first_name=first_name,
                last_name=last_name,
                username=username,
                language_code=language_code,
            )
            updated = await self.user_repository.update_by_telegram_id(
                telegram_id=telegram_id,
                data=update_data,
            )
            return updated or user

        create_data = UserCreate(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code,
        )

        new_user = await self.user_repository.create(create_data)
        if new_user is None:
            self.logger.error(f"Failed to create user with telegram_id={telegram_id}")
            return User(telegram_id=telegram_id, first_name=first_name)

        self.logger.info(f"Created new user: {new_user.display_name} (tg_id={telegram_id})")
        return new_user

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id."""
        return await self.user_repository.get_by_telegram_id(telegram_id)


_user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Получить синглтон сервиса пользователей."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service

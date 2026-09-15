"""
Middleware для инъекции пользователя.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from core.logger import setup_logger

from application.services.user import get_user_service


logger = setup_logger("USER MIDDLEWARE")


class UserMiddleware(BaseMiddleware):
    """Получает или создаёт пользователя и инъектирует в data."""

    def __init__(self) -> None:
        self.user_service = get_user_service()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        # Извлекаем telegram user из события
        telegram_user = None

        if hasattr(event, "message") and event.message and event.message.from_user:
            telegram_user = event.message.from_user
        elif (
            hasattr(event, "callback_query")
            and event.callback_query
            and event.callback_query.from_user
        ):
            telegram_user = event.callback_query.from_user

        if telegram_user:
            user = await self.user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                language_code=telegram_user.language_code,
            )
            data["user"] = user

        return await handler(event, data)

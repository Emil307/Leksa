"""
Middleware для обработки исключений.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from core.logger import setup_logger

from domain.exceptions import BaseDomainException


logger = setup_logger("EXCEPTION MIDDLEWARE")


class ExceptionMiddleware(BaseMiddleware):
    """Перехватывает исключения в хендлерах."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except BaseDomainException as e:
            logger.warning(f"Domain exception: {e.message}")
            # TODO: обработка доменных исключений (отправка сообщения пользователю)
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)

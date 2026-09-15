"""
Middleware для автоматического ответа на callback.
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Update


class CallbackAnswerMiddleware(BaseMiddleware):
    """Автоматически отвечает на callback query после обработки."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            result = await handler(event, data)
        finally:
            # Отвечаем на callback если ещё не ответили
            if hasattr(event, "callback_query") and event.callback_query:
                callback: CallbackQuery = event.callback_query
                try:
                    if not callback.answered:
                        await callback.answer()
                except Exception:
                    pass

        return result

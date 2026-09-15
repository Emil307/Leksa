"""
Кастомный обработчик вебхуков для FastAPI (адаптация aiogram).
"""
import asyncio
import secrets
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status

from aiogram import Bot, Dispatcher
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType

from core.logger import setup_logger


class BaseRequestHandler:
    """Базовый обработчик вебхуков."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        handle_in_background: bool = True,
        **data: Any,
    ) -> None:
        self.dispatcher = dispatcher
        self.handle_in_background = handle_in_background
        self.data = data
        self.logger = setup_logger("WEBHOOK HANDLER")

    def register(self, app: FastAPI, /, path: str, **kwargs: Any) -> None:
        """Регистрация маршрута в FastAPI."""
        app.add_api_route(path=path, endpoint=self.handle, methods=["POST"])

    async def close(self) -> None:
        """Закрытие ресурсов."""
        pass

    async def resolve_bot(self, request: Request) -> Bot:
        """Получить Bot из запроса."""
        raise NotImplementedError

    def verify_secret(self, telegram_secret_token: str, bot: Bot) -> bool:
        """Проверка секретного токена."""
        raise NotImplementedError

    async def _background_feed_update(self, bot: Bot, update: Dict[str, Any]) -> None:
        """Обработка обновления в фоне."""
        result = await self.dispatcher.feed_raw_update(bot=bot, update=update, **self.data)
        if isinstance(result, TelegramMethod):
            await self.dispatcher.silent_call_request(bot=bot, result=result)

    async def _handle_request_background(self, bot: Bot, request: Request) -> Response:
        """Фоновая обработка запроса."""
        asyncio.create_task(
            self._background_feed_update(
                bot=bot,
                update=bot.session.json_loads(await request.body()),
            )
        )
        return Response(
            bot.session.json_dumps({}),
            media_type="application/json",
        )

    async def _handle_request(self, bot: Bot, request: Request) -> None:
        """Синхронная обработка запроса."""
        await self.dispatcher.feed_webhook_update(
            bot,
            bot.session.json_loads(await request.body()),
            **self.data,
        )

    async def handle(self, request: Request) -> Response:
        """Основной обработчик вебхука."""
        bot = await self.resolve_bot(request)

        if not self.verify_secret(
            request.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
            bot,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        if self.handle_in_background:
            return await self._handle_request_background(bot=bot, request=request)

        try:
            await self._handle_request(bot=bot, request=request)
        except Exception as e:
            self.logger.error(f"Webhook request error: {e}")

        return Response(status_code=status.HTTP_200_OK)

    __call__ = handle


class SimpleRequestHandler(BaseRequestHandler):
    """Обработчик вебхука для одного бота."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        handle_in_background: bool = True,
        secret_token: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            dispatcher=dispatcher,
            handle_in_background=handle_in_background,
            **data,
        )
        self.bot = bot
        self.secret_token = secret_token

    def verify_secret(self, telegram_secret_token: str, bot: Bot) -> bool:
        """Проверка секретного токена Telegram."""
        if self.secret_token:
            return secrets.compare_digest(telegram_secret_token, self.secret_token)
        return True

    async def close(self) -> None:
        """Закрытие сессии бота."""
        await self.bot.session.close()

    async def resolve_bot(self, request: Request) -> Bot:
        """Возвращает бота."""
        return self.bot

"""
Менеджер бота для вебхуков.
"""
from typing import Optional

from redis.asyncio import Redis

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from core.config import get_settings
from core.logger import setup_logger

from presentation.bot.handlers import register_bot_handlers
from presentation.bot.middlewares.webhook import SimpleRequestHandler
from presentation.bot.middlewares.callback_answer import CallbackAnswerMiddleware
from presentation.bot.middlewares.exceptions import ExceptionMiddleware
from presentation.bot.middlewares.user import UserMiddleware


class BotManager:
    """Менеджер бота для вебхуков."""

    def __init__(self) -> None:
        self.logger = setup_logger("BOT MANAGER")
        self.settings = get_settings()

        self.bot: Optional[Bot] = None
        self.dispatcher: Optional[Dispatcher] = None
        self.handler: Optional[SimpleRequestHandler] = None
        self.is_initialized: bool = False

        self.initialize()

    def initialize(self) -> None:
        """Инициализация менеджера."""
        if self.is_initialized:
            return

        self.logger.info("Инициализация BotManager")
        self._setup_bot()
        self.is_initialized = True
        self.logger.info("BotManager инициализирован")

    def _setup_bot(self) -> None:
        """Настройка бота."""
        try:
            # Создаем бота
            bot = Bot(
                token=self.settings.bot.token,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    link_preview_is_disabled=True,
                ),
            )

            # Создаем диспетчер с Redis storage
            dp = Dispatcher(
                storage=RedisStorage(
                    redis=Redis(
                        host=self.settings.redis.host,
                        port=self.settings.redis.port,
                        password=self.settings.redis.password or None,
                        db=1,
                    ),
                ),
            )

            # Регистрируем хендлеры
            register_bot_handlers(dp)

            # Middleware (порядок = от внешнего к внутреннему)
            dp.update.middleware(CallbackAnswerMiddleware())
            dp.update.middleware(ExceptionMiddleware())
            dp.update.middleware(UserMiddleware())

            # Создаем хендлер для вебхука
            handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=self.settings.bot.secret_token or None,
            )

            self.bot = bot
            self.dispatcher = dp
            self.handler = handler

            self.logger.info("Бот настроен с Redis FSM Storage")

        except Exception as e:
            self.logger.error(f"Ошибка настройки бота: {e}")

    async def setup_webhook(self, webhook_url: str) -> bool:
        """Настройка вебхука."""
        try:
            if not self.bot:
                self.logger.error("Бот не инициализирован")
                return False

            webhook_info = await self.bot.get_webhook_info()
            if webhook_info.url == webhook_url:
                self.logger.info(f"Вебхук уже установлен: {webhook_url}")
                return True

            await self.bot.set_webhook(
                url=webhook_url,
                secret_token=self.settings.bot.secret_token or None,
            )

            self.logger.info(f"Вебхук установлен: {webhook_url}")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка установки вебхука: {e}")
            return False

    async def remove_webhook(self) -> bool:
        """Удаление вебхука."""
        try:
            if not self.bot:
                return True
            await self.bot.delete_webhook(drop_pending_updates=True)
            self.logger.info("Вебхук удален")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка удаления вебхука: {e}")
            return False


_bot_manager: Optional[BotManager] = None


def get_bot_manager() -> BotManager:
    """Получить синглтон BotManager."""
    global _bot_manager
    if _bot_manager is None:
        _bot_manager = BotManager()
    return _bot_manager

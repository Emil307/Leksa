"""
Точка входа для Telegram бота (FastAPI + webhook).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.logger import setup_logger

from infrastructure.database.base import close_database, init_database

from presentation.bot.manager import get_bot_manager


settings = get_settings()
logger = setup_logger("BOT APP")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    logger.info("🚀 Запуск Webhook...")

    try:
        # Инициализация БД
        await init_database()

        # Инициализируем менеджер бота
        bot_manager = get_bot_manager()
        bot_manager.initialize()

        # Регистрируем маршруты для бота
        webhook_path = "/webhook"
        bot_manager.handler.register(app, path=webhook_path)

        # Устанавливаем вебхук
        await bot_manager.setup_webhook(
            webhook_url=f"{settings.bot.webhook_url}{webhook_path}",
        )

        logger.info("✅ Webhook запущен")

        yield

    finally:
        # Shutdown
        logger.info("🛑 Остановка Webhook...")

        await bot_manager.remove_webhook()
        await close_database()

        logger.info("✅ Webhook остановлен")


def create_app() -> FastAPI:
    """Создание FastAPI приложения для вебхуков."""

    logger.info(f"Starting Bot server on {settings.bot.host}:{settings.bot.port}")
    logger.info(f"Debug mode: {settings.debug}")

    # Создаем приложение
    app = FastAPI(
        debug=settings.debug,
        title=settings.bot.name,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Глобальный обработчик ошибок
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        _logger = setup_logger("BOT APP")
        _logger.error(f"❌ Необработанная ошибка: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app: FastAPI = create_app()

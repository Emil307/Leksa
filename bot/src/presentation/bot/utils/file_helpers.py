"""
Утилиты для работы с файлами и ассетами бота.

Паттерн: FSInputFile для первой отправки → кэширование file_id в Redis → reuse.
"""
import os
from typing import Union, Optional

from aiogram.types import FSInputFile

from core.config import get_settings
from core.logger import setup_logger

from infrastructure.cache.file_cache import get_file_cache


logger = setup_logger("FILE HELPERS")

# Реестр ассетов: логическое имя → файл на диске
IMAGE_ASSETS: dict[str, str] = {
    # Start
    "start_mascot": "mascot_hello.jpg",

    # Menu
    "menu_mascot": "mascot_menu.jpg",

    # Games
    "idiom_start": "idiom_start.jpg",
    "grammar_start": "grammar_start.jpg",

    # Subscription
    "subscription_mascot": "mascot_premium.jpg",
    "subscription_activated": "mascot_premium_activated.jpg",

    # Freemium
    "freemium_offer": "mascot_freemium.jpg",
    "freemium_activated": "mascot_freemium_activated.jpg",

    # Legal
    "legal_mascot": "mascot_legal.jpg",

    # Tests
    "tests_mascot": "mascot_tests.jpg",

    # Games menu
    "games_mascot": "mascot_games.jpg",

    # Gifts
    "gifts_mascot": "mascot_gifts.jpg",

    # Referral
    "referral_mascot": "mascot_referral.jpg",

    # FAQ
    "faq_mascot": "mascot_faq.jpg",
}


def _get_assets_dir() -> str:
    """Получить путь к директории с ассетами."""
    settings = get_settings()
    return str(settings.base_dir / "presentation" / "bot" / "assets")


async def get_image(name: str) -> Union[str, FSInputFile, None]:
    """
    Получить фото для отправки.

    Возвращает:
    - str (file_id) если уже в кэше
    - FSInputFile если файл на диске (первая отправка)
    - None если ассет не найден
    """
    cache = get_file_cache()

    # Проверяем кэш
    file_id = await cache.get_file_id(name)
    if file_id:
        return file_id

    # Получаем путь к файлу
    filename = IMAGE_ASSETS.get(name)
    if not filename:
        logger.warning(f"Asset not found in registry: {name}")
        return None

    path = os.path.join(_get_assets_dir(), filename)
    if not os.path.exists(path):
        logger.warning(f"Asset file not found: {path}")
        return None

    return FSInputFile(path=path, filename=filename)


async def cache_image(name: str, source: Union[str, FSInputFile], file_id: str) -> None:
    """
    Закэшировать file_id после успешной отправки.

    Кэширует только если source — FSInputFile (первая отправка).
    """
    if isinstance(source, str):
        # Уже из кэша, пропускаем
        return

    cache = get_file_cache()
    await cache.set_file_id(name, file_id)
    logger.debug(f"Cached file_id for: {name}")


async def get_game_media(media_file: str) -> Union[str, FSInputFile, None]:
    """
    Получить медиа-файл для вопроса игры (фото или видео).

    media_file — путь относительно assets/games/ (например "idioms/bite_bullet.jpg").
    Использует отдельный namespace в Redis: game_media:{media_file}.
    """
    if not media_file:
        return None

    cache = get_file_cache()
    cache_key = f"game_media:{media_file}"

    # Проверяем кэш
    file_id = await cache.get_file_id(cache_key)
    if file_id:
        return file_id

    # Получаем путь к файлу
    path = os.path.join(_get_assets_dir(), "games", media_file)
    if not os.path.exists(path):
        logger.warning(f"Game media not found: {path}")
        return None

    return FSInputFile(path=path, filename=os.path.basename(media_file))


async def cache_game_media(
    media_file: str,
    source: Union[str, FSInputFile],
    file_id: str,
) -> None:
    """Закэшировать file_id игрового медиа после успешной отправки."""
    if isinstance(source, str):
        return

    cache = get_file_cache()
    await cache.set_file_id(f"game_media:{media_file}", file_id)
    logger.debug(f"Cached game media file_id: {media_file}")

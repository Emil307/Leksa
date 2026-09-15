"""
Утилиты для работы с Telegram API.
"""
from typing import Any, Callable, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from core.logger import setup_logger


logger = setup_logger("TELEGRAM UTILS")


async def safe_send_message(method: Callable, **kwargs: Any) -> Any:
    """Безопасная отправка сообщения через Telegram API."""
    try:
        return await method(**kwargs)
    except Exception as e:
        logger.error(f"Error in safe_send_message: {e}")
        return False


async def send_to_thread(
    bot: Bot,
    chat_id: int,
    text: str,
    thread_id: int = None,
    reply_markup=None,
    parse_mode: str = "HTML",
    user_id: int = None,
    game_type: str = None,
) -> Optional[Message]:
    """
    Отправить сообщение в топик.

    Если топик удалён (TelegramBadRequest) и переданы user_id + game_type,
    пересоздаёт топик и повторяет отправку.
    Если thread_id=None — отправляет в основной чат.
    """
    kwargs = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if thread_id is not None:
        kwargs["message_thread_id"] = thread_id
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    try:
        return await bot.send_message(**kwargs)
    except TelegramBadRequest as e:
        error_msg = str(e).lower()

        # Топик удалён — пересоздаём
        if thread_id and ("thread" in error_msg or "topic" in error_msg or "not found" in error_msg):
            logger.warning(f"Thread {thread_id} deleted, recreating...")

            if user_id and game_type:
                new_thread_id = await _recreate_thread(bot, chat_id, user_id, game_type)

                if new_thread_id:
                    kwargs["message_thread_id"] = new_thread_id
                    try:
                        return await bot.send_message(**kwargs)
                    except Exception as e2:
                        logger.error(f"send_to_thread retry error: {e2}")

            # Не удалось пересоздать — отправляем в основной чат
            kwargs.pop("message_thread_id", None)
            try:
                return await bot.send_message(**kwargs)
            except Exception as e3:
                logger.error(f"send_to_thread fallback error: {e3}")
                return None

        logger.error(f"send_to_thread error: {e}")
        return None
    except Exception as e:
        logger.error(f"send_to_thread error: {e}")
        return None


async def _recreate_thread(
    bot: Bot,
    chat_id: int,
    user_id: int,
    game_type: str,
) -> Optional[int]:
    """Пересоздать Forum Topic для игры и обновить БД."""
    try:
        from application.services.game_thread import get_game_thread_service

        thread_service = get_game_thread_service()
        new_thread_id = await thread_service._create_thread(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            game_type=game_type,
        )
        return new_thread_id
    except Exception as e:
        logger.error(f"_recreate_thread error: {e}")
        return None


async def send_photo_to_thread(
    bot: Bot,
    chat_id: int,
    photo: Any,
    caption: str = None,
    thread_id: int = None,
    reply_markup=None,
    parse_mode: str = "HTML",
) -> Optional[Message]:
    """Отправить фото в топик (или в основной чат если thread_id=None)."""
    kwargs = {
        "chat_id": chat_id,
        "photo": photo,
        "parse_mode": parse_mode,
    }
    if caption is not None:
        kwargs["caption"] = caption
    if thread_id is not None:
        kwargs["message_thread_id"] = thread_id
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    try:
        return await bot.send_photo(**kwargs)
    except Exception as e:
        logger.error(f"send_photo_to_thread error: {e}")
        return None


async def send_video_to_thread(
    bot: Bot,
    chat_id: int,
    video: Any,
    caption: str = None,
    thread_id: int = None,
    reply_markup=None,
    parse_mode: str = "HTML",
) -> Optional[Message]:
    """Отправить видео в топик (или в основной чат если thread_id=None)."""
    kwargs = {
        "chat_id": chat_id,
        "video": video,
        "parse_mode": parse_mode,
        "supports_streaming": True,
    }
    if caption is not None:
        kwargs["caption"] = caption
    if thread_id is not None:
        kwargs["message_thread_id"] = thread_id
    if reply_markup is not None:
        kwargs["reply_markup"] = reply_markup

    try:
        return await bot.send_video(**kwargs)
    except Exception as e:
        logger.error(f"send_video_to_thread error: {e}")
        return None

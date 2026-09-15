"""
Универсальная обёртка для ответов на callback/message.

Определяет тип текущего и нового сообщения (text/photo) и выбирает
оптимальный способ обновления: edit_text, edit_caption, edit_media,
или delete + send new.
"""
from typing import Optional, Union

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    FSInputFile,
)

from core.logger import setup_logger

from presentation.bot.utils.file_helpers import get_image, cache_image


logger = setup_logger("SMART REPLY")


async def smart_callback_reply(
    callback: CallbackQuery,
    *,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    photo_key: Optional[str] = None,
) -> Optional[Message]:
    """
    Умный ответ на callback.

    Определяет, что было в текущем сообщении (текст или фото)
    и что нужно в новом — и выбирает оптимальный способ.

    Args:
        callback: CallbackQuery
        text: Текст сообщения (или caption для фото)
        reply_markup: Inline клавиатура
        photo_key: Ключ ассета (если нужна фотка). None = текстовое сообщение.

    Returns:
        Message | None
    """
    msg: Message = callback.message
    has_photo_now: bool = msg.photo is not None and len(msg.photo) > 0

    # Получаем фото если нужно
    photo = None
    if photo_key:
        photo = await get_image(photo_key)

    need_photo: bool = photo is not None

    try:
        # CASE 1: Было текст → нужен текст → edit_text
        if not has_photo_now and not need_photo:
            return await msg.edit_text(
                text=text,
                reply_markup=reply_markup,
            )

        # CASE 2: Было фото → нужно фото → edit_caption (+ edit_media если фото другое)
        if has_photo_now and need_photo:
            # Пробуем edit_caption (если фото то же)
            try:
                return await msg.edit_caption(
                    caption=text,
                    reply_markup=reply_markup,
                )
            except Exception:
                # Если не получилось — edit_media
                try:
                    media = InputMediaPhoto(media=photo, caption=text, parse_mode="HTML")
                    result = await msg.edit_media(media=media, reply_markup=reply_markup)
                    if result and result.photo and isinstance(photo, FSInputFile):
                        await cache_image(photo_key, photo, result.photo[-1].file_id)
                    return result
                except Exception:
                    pass

        # CASE 3: Структура меняется (текст↔фото) — удаляем + отправляем новое
        try:
            await msg.delete()
        except Exception:
            # Не можем удалить — убираем клавиатуру
            try:
                await msg.edit_reply_markup(reply_markup=None)
            except Exception:
                pass

        # Отправляем новое
        if need_photo:
            sent = await msg.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
            )
            if sent and sent.photo and isinstance(photo, FSInputFile):
                await cache_image(photo_key, photo, sent.photo[-1].file_id)
            return sent
        else:
            return await msg.answer(
                text=text,
                reply_markup=reply_markup,
            )

    except Exception as e:
        logger.error(f"smart_callback_reply error: {e}")
        # Крайний fallback — просто отправить новое
        try:
            if need_photo:
                return await msg.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                )
            return await msg.answer(
                text=text,
                reply_markup=reply_markup,
            )
        except Exception as e2:
            logger.error(f"smart_callback_reply fallback error: {e2}")
            return None


async def send_photo_message(
    message: Message,
    *,
    photo_key: str,
    text: Optional[str] = None,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> Optional[Message]:
    """
    Отправка фото-сообщения из Message (не callback).
    С кэшированием file_id.
    """
    photo = await get_image(photo_key)

    if photo is not None:
        sent = await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=reply_markup,
        )
        if sent and sent.photo and isinstance(photo, FSInputFile):
            await cache_image(photo_key, photo, sent.photo[-1].file_id)
        return sent

    # Fallback — текст без фото
    return await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

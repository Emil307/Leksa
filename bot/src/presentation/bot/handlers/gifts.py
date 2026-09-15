"""Хендлеры для подарков."""

import os

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from domain.entities.user import User

from presentation.bot.config.messages.gifts import (
    GIFTS_MENU,
    GIFT_WORDS_INFO,
    GIFT_PHRASES_INFO,
    GIFT_SUBSCRIBE_REQUIRED,
    GIFT_WORDS_CLAIMED,
    GIFT_PHRASES_CLAIMED,
    GIFT_SUB_30D,
    GIFT_SUB_30D_PAYMENT,
    GIFT_SUB_30D_ACTIVATED,
)
from presentation.bot.config.callbacks.gifts import GiftsCallback, GiftItemCallback
from presentation.bot.config.builders.gifts_builder import GiftsBuilder
from presentation.bot.utils.smart_reply import smart_callback_reply, send_photo_message
from presentation.bot.utils.file_helpers import _get_assets_dir


# Маппинг подарков на тексты
GIFT_INFO_TEXTS = {
    "words": GIFT_WORDS_INFO,
    "phrases": GIFT_PHRASES_INFO,
}

GIFT_CLAIMED_TEXTS = {
    "words": GIFT_WORDS_CLAIMED,
    "phrases": GIFT_PHRASES_CLAIMED,
}

GIFT_PDF_FILES = {
    "words": "gift_1000_words.pdf",
    "phrases": "gift_500_phrases.pdf",
}


# ==============================
# [CALLBACK][GIFTS] Меню подарков
# ==============================
async def process_gifts_menu(
    callback: CallbackQuery,
    callback_data: GiftsCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню подарков."""
    await state.clear()

    if callback_data.new_message:
        await callback.message.edit_reply_markup(reply_markup=None)

        return await send_photo_message(
            message=callback.message,
            text=GIFTS_MENU,
            photo_key="gifts_mascot",
            reply_markup=GiftsBuilder.gifts_menu_keyboard(),
        )

    await smart_callback_reply(
        callback,
        text=GIFTS_MENU,
        photo_key="gifts_mascot",
        reply_markup=GiftsBuilder.gifts_menu_keyboard(),
    )


# ==============================
# [CALLBACK][GIFTS] Выбор подарка / получение
# ==============================
async def process_gift_item(
    callback: CallbackQuery,
    callback_data: GiftItemCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Обработка подарков: info -> subscribe -> claim (PDF)."""
    item: str = callback_data.item

    # --- Подарочная подписка ---
    if item == "sub_30d":
        await smart_callback_reply(
            callback,
            text=GIFT_SUB_30D,
            photo_key="gifts_mascot",
            reply_markup=GiftsBuilder.gift_sub_keyboard(),
        )
        return

    if item == "sub_30d_pay":
        await smart_callback_reply(
            callback,
            text=GIFT_SUB_30D_PAYMENT,
            reply_markup=GiftsBuilder.gift_sub_keyboard(),
        )
        await callback.message.answer(
            text=GIFT_SUB_30D_ACTIVATED,
            reply_markup=GiftsBuilder.gift_sub_activated_keyboard(),
        )
        return

    # --- Шаг 3: Получение подарка (PDF) ---
    if item.endswith("_claim"):
        base_item: str = item.replace("_claim", "")
        claimed_text: str = GIFT_CLAIMED_TEXTS.get(base_item, GIFT_WORDS_CLAIMED)
        pdf_file: str = GIFT_PDF_FILES.get(base_item)

        await callback.message.edit_reply_markup(reply_markup=None)

        if pdf_file:
            pdf_path: str = os.path.join(_get_assets_dir(), pdf_file)
            if os.path.exists(pdf_path):
                await callback.message.answer_document(
                    document=FSInputFile(pdf_path),
                    caption=claimed_text,
                    reply_markup=GiftsBuilder.gift_claimed_keyboard(),
                )
            else:
                await callback.message.answer(
                    text=claimed_text,
                    reply_markup=GiftsBuilder.gift_claimed_keyboard(),
                )
        else:
            await callback.message.answer(
                text=claimed_text,
                reply_markup=GiftsBuilder.gift_claimed_keyboard(),
            )
        return

    # --- Шаг 2: Подписка на канал ---
    if item.endswith("_subscribe"):
        base_item = item.replace("_subscribe", "")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            text=GIFT_SUBSCRIBE_REQUIRED,
            reply_markup=GiftsBuilder.gift_subscribe_keyboard(base_item),
        )
        return

    # --- Шаг 1: Информация о подарке ---
    text: str = GIFT_INFO_TEXTS.get(item, GIFT_WORDS_INFO)
    await smart_callback_reply(
        callback,
        text=text,
        photo_key="gifts_mascot",
        reply_markup=GiftsBuilder.gift_info_keyboard(item),
    )


def register_gifts_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров подарков."""

    dp.callback_query.register(
        process_gifts_menu,
        GiftsCallback.filter(),
    )

    dp.callback_query.register(
        process_gift_item,
        GiftItemCallback.filter(),
    )

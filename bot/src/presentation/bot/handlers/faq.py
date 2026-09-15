"""Хендлеры для FAQ."""

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from domain.entities.user import User

from presentation.bot.config import messages as msg
from presentation.bot.config.callbacks.faq import FAQCallback, FAQItemDetailCallback
from presentation.bot.config.builders.faq_builder import FAQBuilder

from application.services.faq import get_faq_service
from presentation.bot.utils.smart_reply import smart_callback_reply


# ==============================
# [CALLBACK][FAQ] Список вопросов
# ==============================
async def process_faq_list(
    callback: CallbackQuery,
    callback_data: FAQCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ списка вопросов FAQ с пагинацией."""
    await state.clear()

    page: int = callback_data.page
    service = get_faq_service()
    items, total = await service.get_all_items_paginated(page=page)

    if not items and page == 0:
        await smart_callback_reply(
            callback,
            text=msg.FAQ_EMPTY,
            reply_markup=FAQBuilder.questions_keyboard([], 0),
        )
        return

    await smart_callback_reply(
        callback,
        text=msg.FAQ_HEADER,
        photo_key="faq_mascot",
        reply_markup=FAQBuilder.questions_keyboard(items, total, page),
    )


# ==============================
# [CALLBACK][FAQ] Детали вопроса
# ==============================
async def process_faq_item(
    callback: CallbackQuery,
    callback_data: FAQItemDetailCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ ответа на конкретный вопрос."""
    service = get_faq_service()
    item = await service.get_item(callback_data.item_id)

    if not item:
        await callback.answer("Вопрос не найден", show_alert=True)
        return

    await smart_callback_reply(
        callback,
        text=msg.FAQ_ANSWER.format(question=item.question, answer=item.answer),
        reply_markup=FAQBuilder.item_keyboard(),
    )


def register_faq_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров FAQ."""

    dp.callback_query.register(
        process_faq_list,
        FAQCallback.filter(),
    )

    dp.callback_query.register(
        process_faq_item,
        FAQItemDetailCallback.filter(),
    )

"""
Хендлеры для учебных материалов.
"""
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from domain.entities.user import User
from domain.enums.topic import TopicLevel

from presentation.bot.config import messages
from presentation.bot.config.callbacks.educational import (
    EducationalLevelCallback,
    EducationalMenuCallback,
    EducationalSubscribeCheckCallback,
)
from presentation.bot.config.builders.educational import EducationalBuilder

from application.services.educational_topic import get_educational_topic_service
from presentation.bot.utils.smart_reply import smart_callback_reply


# ==============================
# [CALLBACK][EDUCATIONAL] Меню учебных материалов
# ==============================
async def process_educational_menu(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню учебных материалов."""
    await state.clear()

    await smart_callback_reply(
        callback,
        text=messages.EDUCATIONAL_MENU,
        reply_markup=EducationalBuilder.menu_keyboard(),
    )


# ==============================
# [CALLBACK][EDUCATIONAL] Выбор уровня
# ==============================
async def process_educational_level(
    callback: CallbackQuery,
    callback_data: EducationalLevelCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ тем по уровню с пагинацией."""
    level: TopicLevel = TopicLevel(callback_data.level)
    page: int = callback_data.page
    service = get_educational_topic_service()
    topics, total = await service.get_by_level(level.value, page=page)

    header: str = messages.EDUCATIONAL_LEVEL_HEADER.get(level.value, "\U0001f4d6 Материалы")

    if not topics and page == 0:
        await smart_callback_reply(
            callback,
            text=f"{header}\n\n{messages.EDUCATIONAL_NO_TOPICS}",
            reply_markup=EducationalBuilder.menu_keyboard(),
        )
        return

    await smart_callback_reply(
        callback,
        text=header,
        reply_markup=EducationalBuilder.topics_keyboard(topics, total, level.value, page),
    )


# ==============================
# [CALLBACK][EDUCATIONAL] Проверка подписки
# ==============================
async def process_subscribe_check(
    callback: CallbackQuery,
    callback_data: EducationalSubscribeCheckCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Проверка подписки на канал (TODO: реальная проверка)."""
    level: TopicLevel = TopicLevel(callback_data.level)
    await callback.answer("\u2705 Подписка проверена!", show_alert=True)

    service = get_educational_topic_service()
    topics, total = await service.get_by_level(level.value)
    header: str = messages.EDUCATIONAL_LEVEL_HEADER.get(level.value, "\U0001f4d6 Материалы")

    await smart_callback_reply(
        callback,
        text=header,
        reply_markup=EducationalBuilder.topics_keyboard(topics, total, level.value),
    )


def register_educational_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров учебных материалов."""

    dp.callback_query.register(
        process_educational_menu,
        EducationalMenuCallback.filter(),
    )

    dp.callback_query.register(
        process_educational_level,
        EducationalLevelCallback.filter(),
    )

    dp.callback_query.register(
        process_subscribe_check,
        EducationalSubscribeCheckCallback.filter(),
    )

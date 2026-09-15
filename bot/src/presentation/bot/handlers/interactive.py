"""Хендлеры для интерактивных тем."""

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from domain.entities.user import User
from domain.enums.topic import TopicLevel

from presentation.bot.config.messages.interactive import (
    INTERACTIVE_MENU,
    INTERACTIVE_TOPICS_HEADER,
    INTERACTIVE_EMPTY,
)
from presentation.bot.config.callbacks.interactive import (
    InteractiveLevelCallback,
    InteractiveMenuCallback,
)
from presentation.bot.config.builders.interactive_builder import InteractiveBuilder

from application.services.interactive_topic import get_interactive_topic_service
from presentation.bot.utils.smart_reply import smart_callback_reply, send_photo_message


# ==============================
# [CALLBACK][INTERACTIVE] Меню интерактивных тем
# ==============================
async def process_interactive_menu(
    callback: CallbackQuery,
    callback_data: InteractiveMenuCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню интерактивных тем."""
    await state.clear()

    if callback_data.new_message:
        await callback.message.edit_reply_markup(reply_markup=None)

        return await send_photo_message(
            message=callback.message,
            text=INTERACTIVE_MENU,
            photo_key="interactive_mascot",
            reply_markup=InteractiveBuilder.menu_keyboard(),
        )

    await smart_callback_reply(
        callback,
        text=INTERACTIVE_MENU,
        reply_markup=InteractiveBuilder.menu_keyboard(),
    )


# ==============================
# [CALLBACK][INTERACTIVE] Выбор уровня
# ==============================
async def process_interactive_level(
    callback: CallbackQuery,
    callback_data: InteractiveLevelCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ тем по уровню с пагинацией."""
    level: TopicLevel = TopicLevel(callback_data.level)
    page: int = callback_data.page
    service = get_interactive_topic_service()
    topics, total = await service.get_by_level(level.value, page=page)

    header: str = INTERACTIVE_TOPICS_HEADER.format(level=level.get_label())

    if not topics and page == 0:
        await smart_callback_reply(
            callback,
            text=INTERACTIVE_EMPTY,
            reply_markup=InteractiveBuilder.menu_keyboard(),
        )
        return

    await smart_callback_reply(
        callback,
        text=header,
        reply_markup=InteractiveBuilder.topics_keyboard(topics, total, level.value, page),
    )


def register_interactive_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров интерактивных тем."""

    dp.callback_query.register(
        process_interactive_menu,
        InteractiveMenuCallback.filter(),
    )

    dp.callback_query.register(
        process_interactive_level,
        InteractiveLevelCallback.filter(),
    )

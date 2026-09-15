"""
Хендлеры для старта и главного меню.
"""
from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config.callbacks.menu import MenuCallback, StartCallback
from presentation.bot.config.builders.menu import MenuBuilder
from presentation.bot.config.commands import MENU_COMMAND
from presentation.bot.utils.smart_reply import send_photo_message, smart_callback_reply


# ==============================
# [COMMAND] /start — первый экран (текст + кнопка START)
# ==============================
async def process_start_command(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Шаг 1: текстовое сообщение + inline кнопка [START]."""
    await state.clear()

    await send_photo_message(
        message=message,
        photo_key="start_mascot",
        reply_markup=MenuBuilder.reply_keyboard(),
    )

    await message.answer(
        text=MenuBuilder.start_greeting_text(user),
        reply_markup=MenuBuilder.start_greeting_keyboard(),
    )

# ==============================
# [CALLBACK][START] Начать / Показать меню
# ==============================
async def process_start_begin_callback(
    callback: CallbackQuery,
    callback_data: StartCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Шаг 2 (begin): фото + приветствие. Шаг 3 (show_menu): reply keyboard + меню."""
    await state.clear()
    await callback.answer()

    await callback.message.edit_reply_markup(reply_markup=None)

    await send_photo_message(
        message=callback.message,
        text="📋 <b>Главное меню</b>",
        photo_key="menu_mascot",
        reply_markup=MenuBuilder.menu_keyboard(page=0),
    )


# ==============================
# [COMMAND] /menu и кнопка Меню
# ==============================
async def process_menu_command(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Обработка команды /menu или кнопки Меню."""
    await state.clear()

    await send_photo_message(
        message=message,
        text="📋 <b>Главное меню</b>",
        photo_key="menu_mascot",
        reply_markup=MenuBuilder.menu_keyboard(page=0),
    )


# ==============================
# [CALLBACK][MENU] Пагинация меню
# ==============================
async def process_menu_callback(
    callback: CallbackQuery,
    callback_data: MenuCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Пагинация меню — smart_callback_reply обрабатывает и text, и photo."""
    await state.clear()

    if callback_data.new_message:
        await callback.message.edit_reply_markup(reply_markup=None)

        return await send_photo_message(
            message=callback.message,
            text="📋 <b>Главное меню</b>",
            photo_key="menu_mascot",
            reply_markup=MenuBuilder.menu_keyboard(page=callback_data.page),
        )

    await smart_callback_reply(
        callback,
        text="📋 <b>Главное меню</b>",
        photo_key="menu_mascot",
        reply_markup=MenuBuilder.menu_keyboard(page=callback_data.page),
    )


def register_menu_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров меню."""

    dp.message.register(
        process_start_command,
        CommandStart(),
    )

    dp.message.register(
        process_menu_command,
        Command(MENU_COMMAND),
    )

    dp.message.register(
        process_menu_command,
        F.text.in_(["☰ Меню", "🗂 Меню"]),
    )

    dp.callback_query.register(
        process_start_begin_callback,
        StartCallback.filter(),
    )

    dp.callback_query.register(
        process_menu_callback,
        MenuCallback.filter(),
    )

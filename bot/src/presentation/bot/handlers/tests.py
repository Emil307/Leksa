"""
Хендлеры для тестов.
"""
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config import messages
from presentation.bot.config.callbacks.tests import (
    TestDetailCallback,
    TestsMenuCallback,
)
from presentation.bot.config.builders.tests import TestsBuilder
from presentation.bot.utils.smart_reply import send_photo_message, smart_callback_reply


# ==============================
# [CALLBACK][TESTS] Меню тестов
# ==============================
async def process_tests_menu(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню тестов."""
    await state.clear()

    await smart_callback_reply(
        callback,
        text=messages.TESTS_MENU,
        reply_markup=TestsBuilder.menu_keyboard(),
        photo_key="tests_mascot",
    )


# ==============================
# [MESSAGE][TESTS] Кнопка Тесты из reply keyboard
# ==============================
async def process_tests_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка Тесты из reply keyboard."""
    await state.clear()

    await send_photo_message(
        message,
        text=messages.TESTS_MENU,
        photo_key="tests_mascot",
        reply_markup=TestsBuilder.menu_keyboard(),
    )


# ==============================
# [CALLBACK][TESTS] Детали конкретного теста
# ==============================
async def process_test_detail(
    callback: CallbackQuery,
    callback_data: TestDetailCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ деталей конкретного теста.

    Идиомы и карточки теперь запускаются через GameSelectCallback
    напрямую из меню тестов, сюда попадает только eng_level.
    """
    test_type: str = callback_data.test_type

    if test_type == "eng_level":
        await smart_callback_reply(
            callback,
            text=messages.TEST_ENG_LEVEL,
            reply_markup=TestsBuilder.test_detail_keyboard(
                "eng_level", url="https://uwords.ru/test",
            ),
        )


def register_test_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров тестов."""

    dp.message.register(
        process_tests_button,
        F.text.contains("Тесты"),
    )

    dp.callback_query.register(
        process_tests_menu,
        TestsMenuCallback.filter(),
    )

    dp.callback_query.register(
        process_test_detail,
        TestDetailCallback.filter(),
    )

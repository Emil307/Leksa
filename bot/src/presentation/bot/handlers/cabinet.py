"""
Хендлеры для Личного Кабинета — ЗАГЛУШКА.
Статистика и подписка будут из внешнего сервиса.
"""
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config import messages
from presentation.bot.config.callbacks.cabinet import CabinetCallback
from presentation.bot.config.builders.cabinet_builder import CabinetBuilder
from presentation.bot.utils.smart_reply import smart_callback_reply


# ==============================
# [MESSAGE][CABINET]
# Кнопка Кабинет из reply keyboard
# ==============================
async def process_cabinet(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Личный кабинет — заглушка."""
    await state.clear()

    await message.answer(
        text=messages.CABINET,
        reply_markup=CabinetBuilder.keyboard(),
    )


# ==============================
# [CALLBACK][CABINET]
# Callback для Личного Кабинета
# ==============================
async def process_cabinet_callback(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Личный кабинет (callback) — заглушка."""
    await state.clear()

    await smart_callback_reply(
        callback,
        text=messages.CABINET,
        reply_markup=CabinetBuilder.keyboard(),
    )


def register_cabinet_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров кабинета."""

    dp.message.register(
        process_cabinet,
        F.text.contains("Кабинет"),
    )

    dp.callback_query.register(
        process_cabinet_callback,
        CabinetCallback.filter(),
    )

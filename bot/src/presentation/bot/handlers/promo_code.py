"""
Хендлеры для ввода промокодов (FSM).
"""

from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config.messages.promo import (
    PROMO_ENTER,
    PROMO_INVALID,
    PROMO_SUCCESS,
)
from presentation.bot.config.states import PromoCodeState
from presentation.bot.config.builders.subscription_builder import SubscriptionBuilder
from presentation.bot.config.builders.common_builder import CommonBuilder


# ==============================
# [CALLBACK][PROMO] Ввод промокода
# ==============================
async def process_promo_enter(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ экрана ввода промокода и переход в FSM."""
    await state.set_state(PromoCodeState.waiting_for_code)

    await callback.message.edit_text(
        text=PROMO_ENTER,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


# ==============================
# [MESSAGE][PROMO] Обработка введённого промокода
# ==============================
async def process_promo_code_input(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Обработка введённого промокода (мок — любой код валиден)."""
    code: str = message.text.strip()
    await state.clear()

    # Мок: любой непустой промокод считается валидным
    if not code:
        await message.answer(
            text=PROMO_INVALID,
            reply_markup=CommonBuilder.back_to_menu_keyboard(),
        )
        return

    await message.answer(
        text=PROMO_SUCCESS.format(code=code),
        reply_markup=SubscriptionBuilder.subscription_activated_keyboard(),
    )


def register_promo_code_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров промокодов."""

    # Callback: кнопка "Промокоды" из меню подписки
    dp.callback_query.register(
        process_promo_enter,
        F.data == "promo_enter",
    )

    # Callback: кнопка "Ввести промокод" из главного меню
    dp.callback_query.register(
        process_promo_enter,
        F.data == "promo",
    )

    # Message: ввод промокода в FSM
    dp.message.register(
        process_promo_code_input,
        PromoCodeState.waiting_for_code,
    )

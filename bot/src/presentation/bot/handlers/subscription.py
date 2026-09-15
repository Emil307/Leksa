"""
Хендлеры для подписки Premium.
"""

from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config.messages.subscription import (
    SUBSCRIPTION_ACTIVATED,
    SUBSCRIPTION_MENU,
    SUBSCRIPTION_PAYMENT,
)
from presentation.bot.config.callbacks.subscription import (
    SubscriptionCallback,
    SubscriptionPlanCallback,
)
from presentation.bot.config.builders.subscription_builder import SubscriptionBuilder
from presentation.bot.utils.smart_reply import smart_callback_reply, send_photo_message


# ==============================
# [CALLBACK][SUBSCRIPTION] Меню подписки
# ==============================
async def process_subscription_menu(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню подписки с тарифами."""
    await state.clear()

    if callback_data.new_message:
        await callback.message.edit_reply_markup(reply_markup=None)

        return await send_photo_message(
            message=callback.message,
            text=SUBSCRIPTION_MENU,
            photo_key="subscription_mascot",
            reply_markup=SubscriptionBuilder.subscription_menu_keyboard(),
        )

    await smart_callback_reply(
        callback,
        text=SUBSCRIPTION_MENU,
        reply_markup=SubscriptionBuilder.subscription_menu_keyboard(),
        photo_key="subscription_mascot",
    )


# ==============================
# [CALLBACK][SUBSCRIPTION] Выбор тарифа
# ==============================
async def process_subscription_plan(
    callback: CallbackQuery,
    callback_data: SubscriptionPlanCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ экрана оплаты тарифа (мок) + авто-активация."""
    await state.clear()

    months: int = callback_data.months
    price: int = callback_data.price

    # Показываем экран "оплаты"
    await smart_callback_reply(
        callback,
        text=SUBSCRIPTION_PAYMENT.format(months=months, price=price),
        reply_markup=SubscriptionBuilder.subscription_plan_keyboard(months, price),
    )

    # Авто-отправляем сообщение об активации (мок)
    await callback.message.answer(
        text=SUBSCRIPTION_ACTIVATED,
        reply_markup=SubscriptionBuilder.subscription_activated_keyboard(),
    )


# ==============================
# [MESSAGE][PREMIUM] Кнопка Premium из reply keyboard
# ==============================
async def process_subscription_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка Premium — показ меню подписки."""
    await state.clear()

    await message.answer(
        text=SUBSCRIPTION_MENU,
        reply_markup=SubscriptionBuilder.subscription_menu_keyboard(),
    )


def register_subscription_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров подписки."""

    # Кнопка Premium из reply keyboard
    dp.message.register(
        process_subscription_button,
        F.text.contains("Premium"),
    )

    # Callback: меню подписки
    dp.callback_query.register(
        process_subscription_menu,
        SubscriptionCallback.filter(),
    )

    # Callback: выбор тарифа
    dp.callback_query.register(
        process_subscription_plan,
        SubscriptionPlanCallback.filter(),
    )

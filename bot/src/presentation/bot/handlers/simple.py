"""
Хендлеры для простых экранов (support, reviews, channel, legal, premium, promo, etc.).
"""
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User

from presentation.bot.config import messages
from presentation.bot.config.messages.simple import (
    APP_LINK,
    AI_TUTOR,
    DICTIONARY,
    TRANSLATOR,
    TRIAL_OFFER,
    TRIAL_ACTIVATED,
)
from presentation.bot.config.callbacks.common import SimpleActionCallback
from presentation.bot.config.messages.subscription import SUBSCRIPTION_MENU
from presentation.bot.config.builders.common_builder import CommonBuilder
from presentation.bot.config.builders.subscription_builder import SubscriptionBuilder
from presentation.bot.utils.smart_reply import smart_callback_reply


SIMPLE_SCREENS: dict[str, str] = {
    "support": messages.SUPPORT,
    "reviews": messages.REVIEWS,
    "channel": messages.CHANNEL_INFO,
}


# ==============================
# [CALLBACK][SIMPLE] Простые экраны
# ==============================
async def process_simple_callback(
    callback: CallbackQuery,
    callback_data: SimpleActionCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Обработка простых экранов по action."""
    action: str = callback_data.action

    if action == "legal":
        await smart_callback_reply(
            callback,
            text=messages.LEGAL,
            reply_markup=CommonBuilder.legal_keyboard(),
            photo_key="legal_mascot",
        )
        return

    if action == "trial":
        # Предложение триала
        await smart_callback_reply(
            callback,
            text=TRIAL_OFFER,
            reply_markup=CommonBuilder.trial_offer_keyboard(),
            photo_key="freemium_offer",
        )
        return

    if action == "trial_activate":
        # Мок-активация триала
        await smart_callback_reply(
            callback,
            text=TRIAL_ACTIVATED,
            reply_markup=CommonBuilder.trial_activated_keyboard(),
            photo_key="freemium_activated",
        )
        return

    if action == "stub_alert":
        await callback.answer("🚧 Раздел в разработке", show_alert=True)
        return

    if action == "app_open":
        await callback.answer(
            "\U0001f4f1 Открываем приложение...", show_alert=False,
        )
        return

    if action == "premium":
        await smart_callback_reply(
            callback,
            text=SUBSCRIPTION_MENU,
            reply_markup=SubscriptionBuilder.subscription_menu_keyboard(),
        )
        return

    text: str = SIMPLE_SCREENS.get(action, "\U0001f527 Раздел в разработке")
    await smart_callback_reply(
        callback,
        text=text,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


# ==============================
# [MESSAGE] Reply keyboard — Приложение
# ==============================
async def process_app_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка «Приложение» из reply keyboard."""
    await state.clear()

    await message.answer(
        text=APP_LINK,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


# ==============================
# [MESSAGE] Reply keyboard — ИИ-Репетитор
# ==============================
async def process_ai_tutor_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка «ИИ-Репетитор» из reply keyboard."""
    await state.clear()

    await message.answer(
        text=AI_TUTOR,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


# ==============================
# [MESSAGE] Reply keyboard — Словарь
# ==============================
async def process_dictionary_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка «Словарь» из reply keyboard."""
    await state.clear()

    await message.answer(
        text=DICTIONARY,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


# ==============================
# [MESSAGE] Reply keyboard — Переводчик
# ==============================
async def process_translator_button(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Кнопка «Переводчик» из reply keyboard."""
    await state.clear()

    await message.answer(
        text=TRANSLATOR,
        reply_markup=CommonBuilder.back_to_menu_keyboard(),
    )


def register_simple_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров простых экранов."""

    # --- Reply keyboard handlers ---
    dp.message.register(
        process_app_button,
        F.text.contains("Приложение"),
    )
    dp.message.register(
        process_ai_tutor_button,
        F.text.contains("ИИ-Репетитор"),
    )
    dp.message.register(
        process_dictionary_button,
        F.text.contains("Словарь"),
    )
    dp.message.register(
        process_translator_button,
        F.text.contains("Переводчик"),
    )

    # --- Callback query handlers ---
    dp.callback_query.register(
        process_simple_callback,
        SimpleActionCallback.filter(),
    )

"""
Хендлеры для реферальной программы.
"""
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.config import get_settings

from domain.entities.user import User

from presentation.bot.config import messages
from presentation.bot.config.callbacks.referral import ReferralCallback
from presentation.bot.config.builders.referral_builder import ReferralBuilder
from presentation.bot.utils.smart_reply import smart_callback_reply


# ==============================
# [CALLBACK][REFERRAL] Реферальная ссылка
# ==============================
async def process_referral(
    callback: CallbackQuery,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ реферальной ссылки пользователя."""
    await state.clear()

    settings = get_settings()
    referral_link: str = f"{settings.bot.link}?start=ref_{user.telegram_id}"

    await smart_callback_reply(
        callback,
        text=messages.REFERRAL,
        reply_markup=ReferralBuilder.keyboard(referral_link),
        photo_key="referral_mascot",
    )


def register_referral_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров реферальной программы."""

    dp.callback_query.register(
        process_referral,
        ReferralCallback.filter(),
    )

"""Callback data для реферальной программы."""

from aiogram.filters.callback_data import CallbackData


class ReferralCallback(CallbackData, prefix="referral"):
    """Callback для реферальной программы."""

    action: str = "view"

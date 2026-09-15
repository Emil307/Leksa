"""Callback data для личного кабинета."""

from aiogram.filters.callback_data import CallbackData


class CabinetCallback(CallbackData, prefix="cabinet"):
    """Callback для личного кабинета."""

    action: str = "view"

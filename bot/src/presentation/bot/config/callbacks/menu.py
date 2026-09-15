"""Callback data для меню."""

from aiogram.filters.callback_data import CallbackData


class StartCallback(CallbackData, prefix="start"):
    """Callback для старта."""
    pass


class MenuCallback(CallbackData, prefix="menu"):
    """Callback для меню."""

    page: int = 0
    new_message: bool = False

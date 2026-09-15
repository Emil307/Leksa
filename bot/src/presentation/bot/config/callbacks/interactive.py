"""Callback data для интерактивных тем."""

from aiogram.filters.callback_data import CallbackData


class InteractiveMenuCallback(CallbackData, prefix="interactive"):
    """Callback для меню интерактивных тем."""

    new_message: bool = False


class InteractiveLevelCallback(CallbackData, prefix="interactive_level"):
    """Callback для выбора уровня интерактивных тем."""

    level: str
    page: int = 0

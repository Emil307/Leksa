"""Callback data для учебных материалов."""

from aiogram.filters.callback_data import CallbackData


class EducationalMenuCallback(CallbackData, prefix="edu"):
    """Callback для меню учебных материалов."""

    action: str = "menu"


class EducationalLevelCallback(CallbackData, prefix="edu_level"):
    """Callback для выбора уровня."""

    level: str
    page: int = 0


class EducationalSubscribeCheckCallback(CallbackData, prefix="edu_sub_check"):
    """Callback для проверки подписки на канал."""

    level: str

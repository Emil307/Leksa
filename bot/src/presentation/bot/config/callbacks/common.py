"""Callback data для простых экранов."""

from aiogram.filters.callback_data import CallbackData


class SimpleActionCallback(CallbackData, prefix="simple"):
    """Callback для простых действий без отдельного модуля."""

    action: str  # support, reviews, channel, legal, updates, partners, trial, app_open, premium

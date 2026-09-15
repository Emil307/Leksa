"""Callback data для подписки."""

from aiogram.filters.callback_data import CallbackData


class SubscriptionCallback(CallbackData, prefix="sub"):
    """Callback для меню подписки."""

    new_message: bool = False


class SubscriptionPlanCallback(CallbackData, prefix="sub_plan"):
    """Callback для выбора тарифа."""

    months: int
    price: int

"""Callback data для подарков."""

from aiogram.filters.callback_data import CallbackData


class GiftsCallback(CallbackData, prefix="gifts"):
    """Callback для меню подарков."""

    new_message: bool = False


class GiftItemCallback(CallbackData, prefix="gift_item"):
    """Callback для выбора подарка."""

    item: str  # "words" | "phrases" | "sub_30d" | "sub_30d_pay" | "{item}_claim"

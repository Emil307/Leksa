"""Callback data для FAQ."""

from aiogram.filters.callback_data import CallbackData


class FAQCallback(CallbackData, prefix="faq"):
    """Callback для списка вопросов FAQ."""

    page: int = 0


class FAQItemDetailCallback(CallbackData, prefix="faq_item"):
    """Callback для просмотра ответа."""

    item_id: int

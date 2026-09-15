"""Builder для FAQ."""

from typing import List

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from domain.entities.faq import FAQItem
from presentation.bot.config.callbacks.faq import FAQCallback, FAQItemDetailCallback
from presentation.bot.config.callbacks.menu import MenuCallback


class FAQBuilder:
    """Формирование клавиатур для FAQ."""

    @staticmethod
    def questions_keyboard(
        items: List[FAQItem],
        total: int,
        page: int = 0,
        per_page: int = 5,
    ) -> InlineKeyboardMarkup:
        """Клавиатура списка вопросов с пагинацией."""
        builder = InlineKeyboardBuilder()

        for item in items:
            builder.row(InlineKeyboardButton(
                text=item.question[:64],
                callback_data=FAQItemDetailCallback(item_id=item.id).pack(),
            ))

        # Navigation
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=FAQCallback(page=page - 1).pack(),
            ))
        nav.append(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))
        total_pages = (total + per_page - 1) // per_page
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(
                text="Вперёд >",
                style=ButtonStyle.PRIMARY,
                callback_data=FAQCallback(page=page + 1).pack(),
            ))
        builder.row(*nav)

        return builder.as_markup()

    @staticmethod
    def item_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура ответа на вопрос."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=FAQCallback().pack(),
        ))
        return builder.as_markup()

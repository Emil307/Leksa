"""Builder для интерактивных тем."""

from typing import List

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from domain.entities.interactive_topic import InteractiveTopic
from domain.enums.topic import TopicLevel
from presentation.bot.config.callbacks.interactive import (
    InteractiveLevelCallback,
    InteractiveMenuCallback,
)
from presentation.bot.config.callbacks.menu import MenuCallback


class InteractiveBuilder:
    """Формирование клавиатур для интерактивных тем."""

    @staticmethod
    def menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора уровня."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for lvl in TopicLevel:
            builder.row(InlineKeyboardButton(
                text=f"{lvl.get_emoji()} {lvl.get_label()}",
                callback_data=InteractiveLevelCallback(level=lvl.value).pack(),
            ))

        builder.row(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def topics_keyboard(
        topics: List[InteractiveTopic],
        total: int,
        level: str,
        page: int = 0,
        per_page: int = 5,
    ) -> InlineKeyboardMarkup:
        """Клавиатура списка тем с пагинацией."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for topic in topics:
            if topic.url:
                builder.row(InlineKeyboardButton(
                    text=topic.button_text,
                    url=topic.url,
                ))
            else:
                builder.row(InlineKeyboardButton(
                    text=topic.button_text,
                    callback_data=f"interactive_topic_{topic.id}",
                ))

        # --- Навигация ---
        nav_buttons: List[InlineKeyboardButton] = []

        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=InteractiveLevelCallback(
                    level=level,
                    page=page - 1,
                ).pack(),
            ))

        nav_buttons.append(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=InteractiveMenuCallback().pack(),
        ))

        total_pages: int = (total + per_page - 1) // per_page
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(
                text="Вперёд >",
                style=ButtonStyle.PRIMARY,
                callback_data=InteractiveLevelCallback(
                    level=level,
                    page=page + 1,
                ).pack(),
            ))

        builder.row(*nav_buttons)

        return builder.as_markup()

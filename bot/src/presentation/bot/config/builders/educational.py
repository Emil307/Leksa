"""Builder для учебных материалов."""

from typing import List

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from domain.entities.educational_topic import EducationalTopic
from domain.enums.topic import TopicLevel
from presentation.bot.config.callbacks.educational import (
    EducationalLevelCallback,
    EducationalMenuCallback,
    EducationalSubscribeCheckCallback,
)
from presentation.bot.config.callbacks.menu import MenuCallback
from presentation.bot.config.callbacks.tests import TestDetailCallback


class EducationalBuilder:
    """Формирование клавиатур для учебных материалов."""

    @staticmethod
    def menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора уровня."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for lvl in TopicLevel:
            builder.row(InlineKeyboardButton(
                text=f"{lvl.get_label()}",
                callback_data=EducationalLevelCallback(level=lvl.value).pack(),
            ))

        builder.row(InlineKeyboardButton(
            text="Пройти тест ✏",
            callback_data=TestDetailCallback(test_type="eng_level").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def topics_keyboard(
        topics: List[EducationalTopic],
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
                    callback_data=f"topic_{topic.id}",
                ))

        # --- Навигация ---
        nav_buttons: List[InlineKeyboardButton] = []

        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=EducationalLevelCallback(
                    level=level,
                    page=page - 1,
                ).pack(),
            ))

        nav_buttons.append(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=EducationalMenuCallback().pack(),
        ))

        total_pages: int = (total + per_page - 1) // per_page
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(
                text="Вперёд >",
                style=ButtonStyle.PRIMARY,
                callback_data=EducationalLevelCallback(
                    level=level,
                    page=page + 1,
                ).pack(),
            ))

        builder.row(*nav_buttons)

        return builder.as_markup()

    @staticmethod
    def subscribe_keyboard(level: str) -> InlineKeyboardMarkup:
        """Клавиатура проверки подписки на канал."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Наш канал",
            style=ButtonStyle.PRIMARY,
            url="https://t.me/uwords_eng",
        ))
        builder.row(InlineKeyboardButton(
            text="Проверить подписку",
            callback_data=EducationalSubscribeCheckCallback(level=level).pack(),
        ))

        return builder.as_markup()

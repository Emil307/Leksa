"""Builder для тестов."""

from typing import Optional

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.games import GameSelectCallback
from presentation.bot.config.callbacks.menu import MenuCallback
from presentation.bot.config.callbacks.tests import (
    TestDetailCallback,
    TestsMenuCallback,
)


class TestsBuilder:
    """Формирование клавиатур для раздела тестов."""

    @staticmethod
    def menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура меню тестов."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Тест на уровень",
            callback_data=TestDetailCallback(test_type="eng_level").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="Тест на словарный запас",
            callback_data=GameSelectCallback(game="cards", source="tests").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="Тест на идиомы",
            callback_data=GameSelectCallback(game="idioms", source="tests").pack(),
        ))
        builder.row(
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback().pack(),
            ),
            InlineKeyboardButton(
                text="Вперёд >",
                style=ButtonStyle.PRIMARY,
                callback_data=TestsMenuCallback(action="page2").pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def test_detail_keyboard(
        test_type: str,
        url: Optional[str] = None,
    ) -> InlineKeyboardMarkup:
        """Клавиатура деталей теста."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if url:
            builder.row(InlineKeyboardButton(text="🚀 Начать", url=url))
        else:
            builder.row(InlineKeyboardButton(
                text="🚀 Начать",
                callback_data=TestDetailCallback(test_type=test_type).pack(),
            ))

        builder.row(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=TestsMenuCallback(action="menu").pack(),
        ))

        return builder.as_markup()

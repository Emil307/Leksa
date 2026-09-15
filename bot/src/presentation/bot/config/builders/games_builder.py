"""Builder для игр."""

from typing import List

from aiogram.enums import ButtonStyle
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from presentation.bot.config.callbacks.menu import MenuCallback
from presentation.bot.config.callbacks.games import (
    GamesMenuCallback,
    GameSelectCallback,
    GameStartCallback,
    GrammarLevelCallback,
)
from presentation.bot.config.callbacks.tests import TestDetailCallback, TestsMenuCallback
from presentation.bot.config.callbacks.subscription import SubscriptionCallback

from domain.enums.topic import TopicLevel

LETTERS = ["A", "B", "C", "D"]


class GamesBuilder:
    """Формирование клавиатур для раздела игр."""

    # ==============================
    # Меню игр (inline)
    # ==============================

    @staticmethod
    def menu_keyboard(page: int = 0) -> InlineKeyboardMarkup:
        """Клавиатура меню игр."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if page == 0:
            builder.row(InlineKeyboardButton(
                text="🃏 Карточки",
                callback_data=GameSelectCallback(game="cards").pack(),
            ))
            builder.row(InlineKeyboardButton(
                text="🎭 Идиомус",
                callback_data=GameSelectCallback(game="idioms").pack(),
            ))
            builder.row(InlineKeyboardButton(
                text="📝 Грамматикус",
                callback_data=GameSelectCallback(game="grammar").pack(),
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
                    callback_data=GamesMenuCallback(page=1).pack(),
                ),
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text="< Назад",
                    style=ButtonStyle.PRIMARY,
                    callback_data=GamesMenuCallback(page=0).pack(),
                ),
                InlineKeyboardButton(
                    text="☰ Меню",
                    style=ButtonStyle.SUCCESS,
                    callback_data=MenuCallback().pack(),
                ),
            )

        return builder.as_markup()

    # ==============================
    # Стартовые клавиатуры (inline)
    # ==============================

    @staticmethod
    def idiom_start_keyboard(source: str = "games") -> InlineKeyboardMarkup:
        """Inline клавиатура стартового сообщения Идиомуса."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="🚀 Начать",
            callback_data=GameStartCallback(game="idioms", source=source).pack(),
        ))

        if source == "tests":
            builder.row(InlineKeyboardButton(
                text="↩ Вернуться",
                style=ButtonStyle.PRIMARY,
                callback_data=TestsMenuCallback(action="menu").pack(),
            ))
        
        else:
            builder.row(InlineKeyboardButton(
                text="↩ Вернуться",
                style=ButtonStyle.PRIMARY,
                callback_data=GamesMenuCallback().pack(),
            ))

        return builder.as_markup()

    @staticmethod
    def grammar_start_keyboard(source: str = "games") -> InlineKeyboardMarkup:
        """Inline клавиатура стартового сообщения Грамматикуса."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="🚀 Начать",
            callback_data=GameStartCallback(game="grammar", source=source).pack(),
        ))

        if source == "tests":
            builder.row(InlineKeyboardButton(
                text="↩ Вернуться",
                style=ButtonStyle.PRIMARY,
                callback_data=TestsMenuCallback(action="menu").pack(),
            ))
        else:
            builder.row(InlineKeyboardButton(
                text="↩ Вернуться",
                style=ButtonStyle.PRIMARY,
                callback_data=GamesMenuCallback().pack(),
            ))

        return builder.as_markup()

    @staticmethod
    def grammar_level_keyboard(source: str = "games") -> InlineKeyboardMarkup:
        """Inline клавиатура выбора уровня Грамматикуса."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for lvl in TopicLevel:
            builder.row(InlineKeyboardButton(
                text=lvl.get_label(),
                callback_data=GrammarLevelCallback(level=lvl.value, source=source).pack(),
            ))

        builder.row(InlineKeyboardButton(
            text="Тест на уровень ✏",
            style=ButtonStyle.SUCCESS,
            callback_data=TestDetailCallback(test_type="eng_level").pack(),
        ))

        builder.row(
            InlineKeyboardButton(
                text="↩ Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=GameSelectCallback(game="grammar", source=source).pack(),
            ),
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback().pack(),
            ),
        )

        return builder.as_markup()

    # ==============================
    # Inline keyboard для вопросов (в топиках reply keyboard не работает)
    # ==============================

    @staticmethod
    def question_inline_keyboard(game: str) -> InlineKeyboardMarkup:
        """Inline keyboard A/B/C/D + Меню/Пропустить."""
        from presentation.bot.config.callbacks.games import GameAnswerCallback

        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="A",
                callback_data=GameAnswerCallback(game=game, answer="A").pack(),
            ),
            InlineKeyboardButton(
                text="B",
                callback_data=GameAnswerCallback(game=game, answer="B").pack(),
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="C",
                callback_data=GameAnswerCallback(game=game, answer="C").pack(),
            ),
            InlineKeyboardButton(
                text="D",
                callback_data=GameAnswerCallback(game=game, answer="D").pack(),
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback().pack(),
            ),
            InlineKeyboardButton(
                text="⏭ Пропустить",
                style=ButtonStyle.PRIMARY,
                callback_data=GameAnswerCallback(game=game, answer="skip").pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def result_inline_keyboard(source: str = "games") -> InlineKeyboardMarkup:
        """Inline keyboard после результатов (навигация)."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if source == "tests":
            builder.row(
                InlineKeyboardButton(
                    text="☰ Меню",
                    style=ButtonStyle.SUCCESS,
                    callback_data=MenuCallback().pack(),
                ),
                InlineKeyboardButton(
                    text="К Тестам",
                    style=ButtonStyle.PRIMARY,
                    callback_data=TestsMenuCallback(action="menu").pack(),
                ),
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text="☰ Меню",
                    style=ButtonStyle.SUCCESS,
                    callback_data=MenuCallback().pack(),
                ),
                InlineKeyboardButton(
                    text="К Играм",
                    style=ButtonStyle.PRIMARY,
                    callback_data=GamesMenuCallback().pack(),
                ),
            )

        return builder.as_markup()

    # ==============================
    # Inline для результатов (Premium)
    # ==============================

    @staticmethod
    def idiom_result_keyboard() -> InlineKeyboardMarkup:
        """Inline кнопка Premium под результатом Идиомуса."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Оформить Uwords Premium ⭐",
            callback_data=SubscriptionCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def grammar_result_keyboard() -> InlineKeyboardMarkup:
        """Inline кнопка Premium под результатом Грамматикуса."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Оформить Uwords Premium ⭐",
            callback_data=SubscriptionCallback().pack(),
        ))

        return builder.as_markup()

    # ==============================
    # Общие inline
    # ==============================

    @staticmethod
    def back_keyboard(source: str) -> InlineKeyboardMarkup:
        """Inline кнопка назад."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if source == "tests":
            builder.row(InlineKeyboardButton(
                text="↩ К тестам",
                style=ButtonStyle.PRIMARY,
                callback_data=TestsMenuCallback(action="menu").pack(),
            ))
        else:
            builder.row(InlineKeyboardButton(
                text="↩ К играм",
                style=ButtonStyle.PRIMARY,
                callback_data=GamesMenuCallback().pack(),
            ))

        return builder.as_markup()

    @staticmethod
    def cards_stub_keyboard(source: str = "games") -> InlineKeyboardMarkup:
        """Клавиатура заглушки для карточек."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if source == "tests":
            builder.row(
                InlineKeyboardButton(
                    text="↩ К Тестам",
                    style=ButtonStyle.PRIMARY,
                    callback_data=TestsMenuCallback(action="menu").pack(),
                ),
                InlineKeyboardButton(
                    text="☰ Меню",
                    style=ButtonStyle.SUCCESS,
                    callback_data=MenuCallback().pack(),
                ),
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text="↩ К Играм",
                    style=ButtonStyle.PRIMARY,
                    callback_data=GamesMenuCallback().pack(),
                ),
                InlineKeyboardButton(
                    text="☰ Меню",
                    style=ButtonStyle.SUCCESS,
                    callback_data=MenuCallback().pack(),
                ),
            )

        return builder.as_markup()

"""Builder для главного меню."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from aiogram.enums import ButtonStyle
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from domain.entities.user import User
from presentation.bot.config import messages
from presentation.bot.config.callbacks.common import SimpleActionCallback
from presentation.bot.config.callbacks.educational import EducationalMenuCallback
from presentation.bot.config.callbacks.faq import FAQCallback
from presentation.bot.config.callbacks.gifts import GiftsCallback
from presentation.bot.config.callbacks.interactive import InteractiveMenuCallback
from presentation.bot.config.callbacks.menu import MenuCallback, StartCallback
from presentation.bot.config.callbacks.referral import ReferralCallback


class MenuBuilder:
    """Формирование сообщений и клавиатур для меню."""

    @staticmethod
    def start_greeting_text(user: User) -> str:
        """Текст приветствия после нажатия START."""
        name: str = user.first_name or "друг"
        return messages.START_GREETING.format(name=name)

    @staticmethod
    def start_greeting_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после нажатия START (кнопка Начать)."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="🚀 Начать",
                callback_data=StartCallback().pack(),
            )
        )
        return builder.as_markup()

    @staticmethod
    def menu_keyboard(page: int = 0) -> InlineKeyboardMarkup:
        """Inline-клавиатура главного меню."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        if page == 0:
            # --- Основные действия ---
            builder.row(InlineKeyboardButton(
                text="📣 Наш канал",
                url="https://t.me/uwords_eng",
            ))

            builder.row(InlineKeyboardButton(
                text="🎁 Подарки",
                callback_data=GiftsCallback().pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="🔑 Ввести промокод",
                callback_data="promo",
            ))

            builder.row(InlineKeyboardButton(
                text="🔗 Реферальная программа",
                callback_data=ReferralCallback().pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="⭐ 7 дней Uwords Premium бесплатно",
                callback_data=SimpleActionCallback(action="trial").pack(),
            ))

            # --- Навигация ---
            builder.row(InlineKeyboardButton(
                text="Вперёд >",
                style=ButtonStyle.PRIMARY,
                callback_data=MenuCallback(page=1).pack(),
            ))

        elif page == 1:
            builder.row(InlineKeyboardButton(
                text="📚 Учебные материалы",
                callback_data=EducationalMenuCallback().pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="🎮 Интерактивные темы",
                callback_data=InteractiveMenuCallback().pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="❤️ Отзывы",
                url="https://t.me/uwords_reviews",
            ))

            builder.row(InlineKeyboardButton(
                text="❓ FAQ",
                callback_data=FAQCallback().pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="👨‍💻 Поддержка",
                url="https://t.me/uwords_support",
            ))

            # --- Навигация ---
            builder.row(
                InlineKeyboardButton(
                    text="< Назад",
                    style=ButtonStyle.PRIMARY,
                    callback_data=MenuCallback(page=0).pack(),
                ),
                InlineKeyboardButton(
                    text="Вперёд >",
                    style=ButtonStyle.PRIMARY,
                    callback_data=MenuCallback(page=2).pack(),
                )
            )

        else:
            builder.row(InlineKeyboardButton(
                text="📋 Соглашения",
                callback_data=SimpleActionCallback(action="legal").pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="🤝 Партнёрам",
                callback_data=SimpleActionCallback(action="stub_alert").pack(),
            ))

            builder.row(InlineKeyboardButton(
                text="🔄 Обновления",
                callback_data=SimpleActionCallback(action="stub_alert").pack(),
            ))

            # --- Навигация ---
            builder.row(InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=MenuCallback(page=1).pack(),
            ))

        return builder.as_markup()

    @staticmethod
    def reply_keyboard() -> ReplyKeyboardMarkup:
        """Persistent reply-клавиатура."""
        builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

        builder.row(
            KeyboardButton(text="📱 Приложение"),
            KeyboardButton(text="🤖 ИИ-Репетитор"),
        )
        builder.row(
            KeyboardButton(text="✏️ Тесты"),
            KeyboardButton(text="🗂 Меню"),
            KeyboardButton(text="🎮 Игры"),
        )
        builder.row(
            KeyboardButton(text="📖 Словарь"),
            KeyboardButton(text="🏠 Кабинет"),
            KeyboardButton(text="💬 Переводчик"),
        )
        builder.row(
            KeyboardButton(text="⭐ Premium", style=ButtonStyle.PRIMARY),
        )

        return builder.as_markup(resize_keyboard=True)

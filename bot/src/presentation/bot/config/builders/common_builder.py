"""Builder для общих элементов."""

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.common import SimpleActionCallback
from presentation.bot.config.callbacks.menu import MenuCallback


class CommonBuilder:
    """Формирование общих клавиатур."""

    @staticmethod
    def back_to_menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура с кнопкой возврата в меню."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def trial_offer_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура предложения триала."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="⭐ 7 дней Premium бесплатно",
            callback_data=SimpleActionCallback(action="trial_activate").pack(),
        ))

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def trial_activated_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после активации триала."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="📱 Открыть приложение",
            url="https://uwords.ru/app",
        ))

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def legal_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура соглашений."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Политика конфиденциальности",
            url="https://uwords.ru/privacy",
        ))
        
        builder.row(InlineKeyboardButton(
            text="Пользовательское соглашение",
            url="https://uwords.ru/terms",
        ))

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

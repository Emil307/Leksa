"""Builder для личного кабинета."""

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.menu import MenuCallback


class CabinetBuilder:
    """Формирование клавиатур для личного кабинета."""

    @staticmethod
    def keyboard() -> InlineKeyboardMarkup:
        """Клавиатура личного кабинета."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

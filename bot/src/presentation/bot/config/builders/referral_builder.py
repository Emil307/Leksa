"""Builder для реферальной программы."""

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.menu import MenuCallback


class ReferralBuilder:
    """Формирование клавиатур для реферальной программы."""

    @staticmethod
    def keyboard(referral_link: str) -> InlineKeyboardMarkup:
        """Клавиатура реферальной программы."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="Копировать ссылку",
            copy_text=CopyTextButton(text=referral_link),
        ))
        
        builder.row(InlineKeyboardButton(
            text="↩ Вернуться",
            style=ButtonStyle.PRIMARY,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

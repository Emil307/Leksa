"""Builder для подарков."""

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.gifts import GiftsCallback, GiftItemCallback
from presentation.bot.config.callbacks.menu import MenuCallback


class GiftsBuilder:
    """Формирование клавиатур для подарков."""

    @staticmethod
    def gifts_menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура меню подарков."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="🎁 1000 важных слов",
            callback_data=GiftItemCallback(item="words").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="🎁 500 разговорных фраз",
            callback_data=GiftItemCallback(item="phrases").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="🎁 Подарочная подписка на 30 дней",
            callback_data=GiftItemCallback(item="sub_30d").pack(),
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
                callback_data=GiftsCallback(new_message=True).pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def gift_info_keyboard(item: str) -> InlineKeyboardMarkup:
        """Клавиатура с кнопкой Забрать подарок (первый шаг)."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="🎁 Забрать подарок",
            callback_data=GiftItemCallback(item=f"{item}_subscribe").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="↩ Назад",
            style=ButtonStyle.PRIMARY,
            callback_data=GiftsCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def gift_subscribe_keyboard(item: str) -> InlineKeyboardMarkup:
        """Клавиатура подписки на канал + забрать подарок."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="📺 Наш канал",
            url="https://t.me/uwords_eng",
        ))
        builder.row(InlineKeyboardButton(
            text="🎁 Забрать подарок",
            callback_data=GiftItemCallback(item=f"{item}_claim").pack(),
        ))
        builder.row(
            InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=GiftItemCallback(item=item).pack(),
            ),
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback().pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def gift_claimed_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после получения подарка."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="< Назад",
                style=ButtonStyle.PRIMARY,
                callback_data=GiftsCallback(new_message=True).pack(),
            ),
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback(new_message=True).pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def gift_sub_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура подарочной подписки."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="💳 Оплатить",
            callback_data=GiftItemCallback(item="sub_30d_pay").pack(),
        ))
        builder.row(InlineKeyboardButton(
            text="↩ Назад",
            style=ButtonStyle.PRIMARY,
            callback_data=GiftsCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def gift_sub_activated_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после активации подарочной подписки."""
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

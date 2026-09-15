"""Builder для подписки Premium."""

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from presentation.bot.config.callbacks.menu import MenuCallback
from presentation.bot.config.callbacks.subscription import (
    SubscriptionCallback,
    SubscriptionPlanCallback,
)


# Тарифы: (месяцы, цена за месяц, полная цена, скидка)
PLANS = [
    (1, 499, 499, None),
    (3, 399, 1197, "-20%"),
    (6, 349, 2094, "-30%"),
    (12, 299, 3588, "-40%"),
]


class SubscriptionBuilder:
    """Формирование клавиатур для подписки."""

    @staticmethod
    def subscription_menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура меню подписки с тарифами."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for months, per_month, total, discount in PLANS:
            label = f"Premium {months} мес. — {total} ₽"
            if discount:
                label += f" ({discount})"

            builder.row(InlineKeyboardButton(
                text=label,
                callback_data=SubscriptionPlanCallback(
                    months=months,
                    price=total,
                ).pack(),
            ))

        builder.row(InlineKeyboardButton(
            text="☰ Меню",
            style=ButtonStyle.SUCCESS,
            callback_data=MenuCallback().pack(),
        ))

        return builder.as_markup()

    @staticmethod
    def subscription_plan_keyboard(months: int, price: int) -> InlineKeyboardMarkup:
        """Клавиатура оплаты тарифа."""
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text="💳 Оплатить",
            url="https://uwords.ru/pay/mock",
        ))

        builder.row(InlineKeyboardButton(
            text="Обновить ссылку 🔄",
            callback_data=SubscriptionPlanCallback(
                months=months,
                price=price,
            ).pack(),
        ))

        builder.row(
            InlineKeyboardButton(
                text="☰ Меню",
                style=ButtonStyle.SUCCESS,
                callback_data=MenuCallback().pack(),
            ),
            InlineKeyboardButton(
                text="↩ Вернуться",
                style=ButtonStyle.PRIMARY,
                callback_data=SubscriptionCallback().pack(),
            ),
        )

        return builder.as_markup()

    @staticmethod
    def subscription_activated_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура после активации Premium."""
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

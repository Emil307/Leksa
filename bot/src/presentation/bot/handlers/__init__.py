"""
Регистрация всех хендлеров бота.
"""
from aiogram import Dispatcher

from presentation.bot.handlers.menu import register_menu_handlers
from presentation.bot.handlers.tests import register_test_handlers
from presentation.bot.handlers.educational import register_educational_handlers
from presentation.bot.handlers.interactive import register_interactive_handlers
from presentation.bot.handlers.subscription import register_subscription_handlers
from presentation.bot.handlers.promo_code import register_promo_code_handlers
from presentation.bot.handlers.gifts import register_gifts_handlers
from presentation.bot.handlers.cabinet import register_cabinet_handlers
from presentation.bot.handlers.referral import register_referral_handlers
from presentation.bot.handlers.faq import register_faq_handlers
from presentation.bot.handlers.games import register_games_handlers
from presentation.bot.handlers.simple import register_simple_handlers


def register_bot_handlers(dp: Dispatcher) -> None:
    """Регистрация всех хендлеров."""
    register_menu_handlers(dp)
    register_test_handlers(dp)
    register_educational_handlers(dp)
    register_interactive_handlers(dp)
    register_subscription_handlers(dp)
    register_promo_code_handlers(dp)
    register_gifts_handlers(dp)
    register_cabinet_handlers(dp)
    register_referral_handlers(dp)
    register_faq_handlers(dp)
    register_games_handlers(dp)
    register_simple_handlers(dp)

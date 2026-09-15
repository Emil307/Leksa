"""Callback data для бота."""

from presentation.bot.config.callbacks.menu import StartCallback, MenuCallback
from presentation.bot.config.callbacks.tests import (
    TestsMenuCallback,
    TestDetailCallback,
    IdiomAnswerCallback,
)
from presentation.bot.config.callbacks.educational import (
    EducationalMenuCallback,
    EducationalLevelCallback,
    EducationalSubscribeCheckCallback,
)
from presentation.bot.config.callbacks.games import (
    GamesMenuCallback,
    GameSelectCallback,
    GameStartCallback,
    GrammarLevelCallback,
)
from presentation.bot.config.callbacks.cabinet import CabinetCallback
from presentation.bot.config.callbacks.referral import ReferralCallback
from presentation.bot.config.callbacks.faq import (
    FAQCallback,
    FAQItemDetailCallback,
)
from presentation.bot.config.callbacks.interactive import (
    InteractiveMenuCallback,
    InteractiveLevelCallback,
)
from presentation.bot.config.callbacks.common import SimpleActionCallback
from presentation.bot.config.callbacks.subscription import (
    SubscriptionCallback,
    SubscriptionPlanCallback,
)
from presentation.bot.config.callbacks.gifts import GiftsCallback, GiftItemCallback

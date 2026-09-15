"""Callback data для игр."""

from aiogram.filters.callback_data import CallbackData


class GamesMenuCallback(CallbackData, prefix="games"):
    """Callback для меню игр."""

    page: int = 0


class GameSelectCallback(CallbackData, prefix="game_select"):
    """Callback для выбора игры."""

    game: str  # "cards" | "idioms" | "grammar"
    source: str = "games"  # "games" | "tests"


class GameStartCallback(CallbackData, prefix="game_start"):
    """Callback для кнопки Начать в стартовом сообщении."""

    game: str  # "idioms" | "grammar"
    source: str = "games"


class GrammarLevelCallback(CallbackData, prefix="grammar_lvl"):
    """Callback для выбора уровня Грамматикуса."""

    level: str  # "beginner" | "intermediate" | "advanced"
    source: str = "games"


class GameAnswerCallback(CallbackData, prefix="game_ans"):
    """Callback для ответа на вопрос в топике (inline кнопки A/B/C/D/Skip)."""

    game: str  # "idioms" | "grammar"
    answer: str  # "A" | "B" | "C" | "D" | "skip"

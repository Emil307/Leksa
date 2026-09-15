"""Callback data для тестов."""

from aiogram.filters.callback_data import CallbackData


class TestsMenuCallback(CallbackData, prefix="tests"):
    """Callback для меню тестов."""

    action: str = "menu"


class TestDetailCallback(CallbackData, prefix="test_detail"):
    """Callback для выбора теста."""

    test_type: str  # eng_level, vocabulary, idioms


class IdiomAnswerCallback(CallbackData, prefix="idiom_ans"):
    """Callback для ответа на вопрос теста идиом."""

    question_idx: int
    answer_idx: int

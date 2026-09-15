"""Константы бота."""

from typing import Dict


class PaginationConstants:
    """Настройки пагинации."""

    DEFAULT_ITEMS_PER_PAGE: int = 5
    DEFAULT_ITEMS_PER_ROW: int = 1


class ButtonTexts:
    """Тексты кнопок."""

    PREV_PAGE: str = "⬅️"
    NEXT_PAGE: str = "➡️"
    BACK: str = "↩ Вернуться"
    BACK_TO_MENU: str = "↩ Вернуться в меню"
    FORWARD: str = "Вперёд >"
    BACKWARD: str = "< Назад"


# --- Rate limiting ---

METHOD_LIMITS: Dict[str, Dict[str, int]] = {
    "sendMessage": {"rate": 30, "window_ms": 1000},
    "sendPhoto": {"rate": 30, "window_ms": 1000},
    "editMessageText": {"rate": 20, "window_ms": 1000},
    "editMessageReplyMarkup": {"rate": 20, "window_ms": 1000},
    "answerCallbackQuery": {"rate": 60, "window_ms": 1000},
}

FAMILY_LIMITS: Dict[str, Dict[str, int]] = {
    "send": {"rate": 30, "window_ms": 1000},
    "edit": {"rate": 20, "window_ms": 1000},
    "answer": {"rate": 60, "window_ms": 1000},
}

METHOD_FAMILY: Dict[str, str] = {
    "sendMessage": "send",
    "sendPhoto": "send",
    "sendVideo": "send",
    "sendDocument": "send",
    "sendAudio": "send",
    "sendMediaGroup": "send",
    "editMessageText": "edit",
    "editMessageReplyMarkup": "edit",
    "editMessageCaption": "edit",
    "answerCallbackQuery": "answer",
}

CHAT_BURST_LIMIT: int = 1
CHAT_BURST_WINDOW_MS: int = 1000
CHAT_OVERFLOW_WAIT_SEC: float = 1.0

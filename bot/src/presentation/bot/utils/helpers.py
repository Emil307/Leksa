"""
Вспомогательные функции.
"""
from typing import Optional


def get_start_param(text: Optional[str]) -> Optional[str]:
    """Извлечь параметр из /start команды."""
    if not text:
        return None

    parts: list[str] = text.split()
    if len(parts) > 1:
        return parts[1]

    return None

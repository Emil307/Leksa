"""
Перечисления для игр.
"""
from enum import Enum


class GameSessionStatus(str, Enum):
    """Статус игровой сессии."""
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"

    def get_label(self) -> str:
        """Человекочитаемое название."""
        labels = {
            self.in_progress: "В процессе",
            self.completed: "Завершена",
            self.abandoned: "Прервана",
        }
        return labels.get(self, self.value)

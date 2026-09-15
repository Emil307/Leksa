"""
Перечисления для учебных тем.
"""
from enum import Enum


class TopicLevel(str, Enum):
    """Уровень сложности темы."""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

    def get_label(self) -> str:
        """Человекочитаемое название."""
        labels = {
            self.beginner: "Beginner — Elementary 🥉",
            self.intermediate: "Intermediate — Upper-Intermediate 🥈",
            self.advanced: "Advanced — Proficiency 🏅",
        }
        return labels.get(self, self.value)

    def get_emoji(self) -> str:
        """Эмодзи уровня."""
        emojis = {
            self.beginner: "🥉",
            self.intermediate: "🥈",
            self.advanced: "🏅",
        }
        return emojis.get(self, "")

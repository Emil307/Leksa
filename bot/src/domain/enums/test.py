"""
Перечисления для тестов.
"""
from enum import Enum


class TestType(str, Enum):
    """Тип теста."""
    eng_level = "eng_level"
    vocabulary = "vocabulary"
    idioms = "idioms"

    def get_label(self) -> str:
        """Человекочитаемое название."""
        labels = {
            self.eng_level: "Уровень английского",
            self.vocabulary: "Словарный запас",
            self.idioms: "Идиомы",
        }
        return labels.get(self, self.value)

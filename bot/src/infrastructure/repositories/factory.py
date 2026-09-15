"""Фабрика репозиториев."""

from infrastructure.repositories.models.user import UserRepository
from infrastructure.repositories.models.educational_topic import EducationalTopicRepository
from infrastructure.repositories.models.interactive_topic import InteractiveTopicRepository
from infrastructure.repositories.models.faq import FAQCategoryRepository, FAQItemRepository
from infrastructure.repositories.models.game import GameRepository, GameSessionRepository
from infrastructure.repositories.models.test_result import TestResultRepository
from infrastructure.repositories.models.idiom import IdiomRepository
from infrastructure.repositories.models.grammar_question import GrammarQuestionRepository
from infrastructure.repositories.models.user_game_thread import UserGameThreadRepository

_instances: dict = {}


def _get(key: str, cls: type) -> object:
    """Получить или создать синглтон репозитория."""
    if key not in _instances:
        _instances[key] = cls()
    return _instances[key]


def get_user_repository() -> UserRepository:
    return _get("user", UserRepository)


def get_educational_topic_repository() -> EducationalTopicRepository:
    return _get("educational_topic", EducationalTopicRepository)


def get_interactive_topic_repository() -> InteractiveTopicRepository:
    return _get("interactive_topic", InteractiveTopicRepository)


def get_faq_category_repository() -> FAQCategoryRepository:
    return _get("faq_category", FAQCategoryRepository)


def get_faq_item_repository() -> FAQItemRepository:
    return _get("faq_item", FAQItemRepository)


def get_game_repository() -> GameRepository:
    return _get("game", GameRepository)


def get_game_session_repository() -> GameSessionRepository:
    return _get("game_session", GameSessionRepository)


def get_test_result_repository() -> TestResultRepository:
    return _get("test_result", TestResultRepository)


def get_idiom_repository() -> IdiomRepository:
    return _get("idiom", IdiomRepository)


def get_grammar_question_repository() -> GrammarQuestionRepository:
    return _get("grammar_question", GrammarQuestionRepository)


def get_user_game_thread_repository() -> UserGameThreadRepository:
    return _get("user_game_thread", UserGameThreadRepository)

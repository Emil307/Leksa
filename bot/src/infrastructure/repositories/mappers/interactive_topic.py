"""Маппер интерактивных тем."""

from domain.entities.interactive_topic import InteractiveTopic
from infrastructure.database.models.interactive_topic import InteractiveTopicModel
from infrastructure.repositories.mappers._base import BaseMapper


class InteractiveTopicMapper(BaseMapper[InteractiveTopic, InteractiveTopicModel]):
    """Маппер InteractiveTopic <-> InteractiveTopicModel."""

    domain_class = InteractiveTopic


def get_interactive_topic_mapper() -> InteractiveTopicMapper:
    """Получить экземпляр маппера интерактивных тем."""
    return InteractiveTopicMapper()

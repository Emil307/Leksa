"""Маппер учебных материалов."""

from domain.entities.educational_topic import EducationalTopic
from infrastructure.database.models.educational_topic import EducationalTopicModel
from infrastructure.repositories.mappers._base import BaseMapper


class EducationalTopicMapper(BaseMapper[EducationalTopic, EducationalTopicModel]):
    """Маппер EducationalTopic <-> EducationalTopicModel."""

    domain_class = EducationalTopic


def get_educational_topic_mapper() -> EducationalTopicMapper:
    """Получить экземпляр маппера учебных тем."""
    return EducationalTopicMapper()

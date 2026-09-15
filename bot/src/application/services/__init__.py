"""Сервисы приложения."""

from application.services.user import UserService, get_user_service
from application.services.educational_topic import EducationalTopicService, get_educational_topic_service
from application.services.interactive_topic import InteractiveTopicService, get_interactive_topic_service
from application.services.faq import FAQService, get_faq_service
from application.services.game import GameService, get_game_service
from application.services.test import TestService, get_test_service
from application.services.idiom import IdiomService, get_idiom_service
from application.services.grammar_question import GrammarQuestionService, get_grammar_question_service

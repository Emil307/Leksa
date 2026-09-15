import pytest
from statements.configuration_startup_statements import ConfigurationStartupStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestConfigurationStartupAcceptance(AbstractBackendTest):
    """Инфраструктурный сценарий 4.1: приложение не стартует с негодной конфигурацией и называет переменную.

    Дано переменная <переменная> имеет вид <вид>
    Когда приложение запускается
    Тогда запуск прерывается
    И сообщение называет недостающую или негодную переменную
    И рабочего значения по умолчанию в поставке нет
    """

    def test_should_start_when_the_whole_configuration_is_supplied(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempt = configuration_startup_statements.start_with_the_complete_configuration()

        configuration_startup_statements.assert_the_application_started(attempt)

    def test_should_refuse_to_start_when_the_access_token_signing_secret_is_absent_or_empty(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_access_token_secret()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(
        reason="RED: приложение стартует без REDIS_HOST — в поставке осталось рабочее значение по умолчанию localhost"
    )
    def test_should_refuse_to_start_when_the_challenge_store_connection_is_absent_or_empty(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_challenge_store_connection()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(reason="RED: переменной MAIL_TEMPLATE_NAMESPACE нет в поставке, приложение стартует без неё")
    def test_should_refuse_to_start_when_the_mail_template_namespace_is_absent_or_empty(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_mail_template_namespace()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(
        reason="RED: приложение стартует без AUTH_CHALLENGE_MAX_ATTEMPTS — остаётся значение по умолчанию 5"
    )
    def test_should_refuse_to_start_when_the_attempt_limit_is_zero_or_negative(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_attempt_limit()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(
        reason="RED: приложение стартует без AUTH_CHALLENGE_TTL_SECONDS — остаётся значение по умолчанию 300"
    )
    def test_should_refuse_to_start_when_the_code_ttl_is_negative_or_non_numeric(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_code_ttl()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(
        reason="RED: приложение стартует без AUTH_CHALLENGE_RESEND_COOLDOWN_SECONDS — остаётся значение по умолчанию 60"
    )
    def test_should_refuse_to_start_when_the_resend_cooldown_is_negative_or_non_numeric(
        self, configuration_startup_statements: ConfigurationStartupStatements
    ):
        attempts = configuration_startup_statements.start_with_each_bad_form_of_the_resend_cooldown()

        configuration_startup_statements.assert_every_start_was_refused_naming_the_variable(attempts)

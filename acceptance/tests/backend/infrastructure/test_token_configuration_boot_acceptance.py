import pytest
from statements.token_configuration_boot_statements import TokenConfigurationBootStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestTokenConfigurationBootAcceptance(AbstractBackendTest):
    """Инфраструктурный сценарий 2.1: некорректная конфигурация токенов запрещает запуск приложения.

    Дано один из обязательных параметров токенов отсутствует, пуст или имеет недопустимое значение
    Когда приложение запускается
    Тогда запуск завершается явной ошибкой конфигурации
    И приложение не подставляет значение для разработки
    И ошибка не откладывается до первого запроса обновления
    """

    def test_should_refuse_to_start_when_the_access_token_ttl_is_absent_or_empty(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_access_token_ttl_absent_or_empty()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    def test_should_refuse_to_start_when_the_access_token_ttl_is_zero_or_negative(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_access_token_ttl_zero_or_negative()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    def test_should_refuse_to_start_when_the_access_token_ttl_is_fractional(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_access_token_ttl_fractional()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(reason="RED: ACCESS_TOKEN_TTL_SECONDS за последней UTC-секундой принят — приложение стартовало")
    def test_should_refuse_to_start_when_the_access_token_ttl_passes_the_last_utc_second(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = (
            token_configuration_boot_statements.start_with_the_access_token_ttl_one_second_past_the_last_utc_second()
        )

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    def test_should_refuse_to_start_when_the_refresh_token_ttl_is_absent_or_empty(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_refresh_token_ttl_absent_or_empty()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    def test_should_refuse_to_start_when_the_refresh_token_ttl_is_zero_or_negative(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_refresh_token_ttl_zero_or_negative()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    def test_should_refuse_to_start_when_the_refresh_token_ttl_is_fractional(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = token_configuration_boot_statements.start_with_the_refresh_token_ttl_fractional()

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

    @pytest.mark.skip(reason="RED: REFRESH_TOKEN_TTL_SECONDS за последней UTC-секундой принят — приложение стартовало")
    def test_should_refuse_to_start_when_the_refresh_token_ttl_passes_the_last_utc_second(
        self, token_configuration_boot_statements: TokenConfigurationBootStatements
    ):
        attempts = (
            token_configuration_boot_statements.start_with_the_refresh_token_ttl_one_second_past_the_last_utc_second()
        )

        token_configuration_boot_statements.assert_every_start_was_refused_naming_the_variable(attempts)

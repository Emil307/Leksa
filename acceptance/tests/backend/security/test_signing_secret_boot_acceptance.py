from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from statements.signing_secret_boot_statements import (
    BLANK_SECRET,
    WHITESPACE_SECRET,
    SigningSecretBootStatements,
)

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def signing_secret_boot_statements() -> Iterator[SigningSecretBootStatements]:
    with TemporaryDirectory() as deployment_directory:
        yield SigningSecretBootStatements(Path(deployment_directory))


class TestSigningSecretBootAcceptance(AbstractBackendTest):
    """Сценарий 4.3: отсутствующий или пустой секрет подписи ломает старт.

    Дано секрет подписи access-токена имеет значение <значение>
    Когда приложение запускается
    Тогда запуск завершается явной ошибкой конфигурации
    И рабочее значение по умолчанию не используется
    """

    def test_should_refuse_to_start_when_the_signing_secret_variable_is_absent(
        self, signing_secret_boot_statements: SigningSecretBootStatements
    ):
        signing_secret_boot_statements.given_the_signing_secret_variable_is_absent()

        signing_secret_boot_statements.when_the_application_starts()

        signing_secret_boot_statements.assert_startup_failed_with_an_explicit_configuration_error()
        signing_secret_boot_statements.assert_no_working_default_was_used()

    def test_should_refuse_to_start_when_the_signing_secret_is_an_empty_string(
        self, signing_secret_boot_statements: SigningSecretBootStatements
    ):
        signing_secret_boot_statements.given_the_signing_secret_is(BLANK_SECRET)

        signing_secret_boot_statements.when_the_application_starts()

        signing_secret_boot_statements.assert_startup_failed_with_an_explicit_configuration_error()
        signing_secret_boot_statements.assert_no_working_default_was_used()

    @pytest.mark.skip(reason="RED: whitespace-only JWT_SECRET still boots the application")
    def test_should_refuse_to_start_when_the_signing_secret_is_only_whitespace(
        self, signing_secret_boot_statements: SigningSecretBootStatements
    ):
        signing_secret_boot_statements.given_the_signing_secret_is(WHITESPACE_SECRET)

        signing_secret_boot_statements.when_the_application_starts()

        signing_secret_boot_statements.assert_startup_failed_with_an_explicit_configuration_error()
        signing_secret_boot_statements.assert_no_working_default_was_used()

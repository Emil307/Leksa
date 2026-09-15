import tempfile
from dataclasses import dataclass
from pathlib import Path

from statements.jvm_configuration_probe import run_configuration_probe

ACCESS_TOKEN_SECRET = "JWT_SECRET"
CHALLENGE_STORE_CONNECTION = "REDIS_HOST"
MAIL_TEMPLATE_NAMESPACE = "MAIL_TEMPLATE_NAMESPACE"
ATTEMPT_LIMIT = "AUTH_CHALLENGE_MAX_ATTEMPTS"
CODE_TTL = "AUTH_CHALLENGE_TTL_SECONDS"
RESEND_COOLDOWN = "AUTH_CHALLENGE_RESEND_COOLDOWN_SECONDS"
ACCESS_TOKEN_TTL = "ACCESS_TOKEN_TTL_SECONDS"
REFRESH_TOKEN_TTL = "REFRESH_TOKEN_TTL_SECONDS"

COMPLETE_CONFIGURATION = {
    ACCESS_TOKEN_SECRET: "acceptance-signing-secret",
    CHALLENGE_STORE_CONNECTION: "localhost",
    MAIL_TEMPLATE_NAMESPACE: "acceptance",
    ATTEMPT_LIMIT: "5",
    CODE_TTL: "300",
    RESEND_COOLDOWN: "60",
    ACCESS_TOKEN_TTL: "900",
    REFRESH_TOKEN_TTL: "1209600",
}
ABSENT_FORM = "отсутствует"
EMPTY_VALUE = ""
ZERO_VALUE = "0"
NEGATIVE_VALUE = "-1"
NON_NUMERIC_VALUE = "not-a-number"
COMPLETE_FORM = "полная конфигурация"
STDERR_EXCERPT_CHARACTERS = 600


@dataclass(frozen=True)
class StartupAttempt:
    variable: str
    form: str
    exit_code: int
    stderr: str


class ConfigurationStartupStatements:
    def start_with_the_complete_configuration(self) -> StartupAttempt:
        return self._start(COMPLETE_CONFIGURATION, COMPLETE_FORM, COMPLETE_FORM)

    def start_with_each_bad_form_of_the_access_token_secret(self) -> list[StartupAttempt]:
        return self._absent_and_empty(ACCESS_TOKEN_SECRET)

    def start_with_each_bad_form_of_the_challenge_store_connection(self) -> list[StartupAttempt]:
        return self._absent_and_empty(CHALLENGE_STORE_CONNECTION)

    def start_with_each_bad_form_of_the_mail_template_namespace(self) -> list[StartupAttempt]:
        return self._absent_and_empty(MAIL_TEMPLATE_NAMESPACE)

    def start_with_each_bad_form_of_the_attempt_limit(self) -> list[StartupAttempt]:
        return self._absent_and_invalid(ATTEMPT_LIMIT, [ZERO_VALUE, NEGATIVE_VALUE])

    def start_with_each_bad_form_of_the_code_ttl(self) -> list[StartupAttempt]:
        return self._absent_and_invalid(CODE_TTL, [NEGATIVE_VALUE, NON_NUMERIC_VALUE])

    def start_with_each_bad_form_of_the_resend_cooldown(self) -> list[StartupAttempt]:
        return self._absent_and_invalid(RESEND_COOLDOWN, [NEGATIVE_VALUE, NON_NUMERIC_VALUE])

    def assert_the_application_started(self, attempt: StartupAttempt) -> None:
        assert attempt.exit_code == 0, (
            f"приложение не стартовало с полной конфигурацией: {attempt.stderr[-STDERR_EXCERPT_CHARACTERS:]}"
        )

    def assert_every_start_was_refused_naming_the_variable(self, attempts: list[StartupAttempt]) -> None:
        for attempt in attempts:
            self._assert_start_was_refused(attempt)
            self._assert_message_names_the_variable(attempt)

    def _assert_start_was_refused(self, attempt: StartupAttempt) -> None:
        assert attempt.exit_code != 0, (
            f"приложение стартовало, хотя переменная {attempt.variable} {attempt.form}: "
            "в поставке осталось рабочее значение по умолчанию"
        )

    def _assert_message_names_the_variable(self, attempt: StartupAttempt) -> None:
        assert attempt.variable in attempt.stderr, (
            f"сообщение не называет переменную {attempt.variable} ({attempt.form}): "
            f"{attempt.stderr[-STDERR_EXCERPT_CHARACTERS:]}"
        )

    def _absent_and_empty(self, variable: str) -> list[StartupAttempt]:
        return self._absent_and_invalid(variable, [EMPTY_VALUE])

    def _absent_and_invalid(self, variable: str, values: list[str]) -> list[StartupAttempt]:
        attempts = [self._start(self._configuration_without(variable), variable, ABSENT_FORM)]
        for value in values:
            attempts.append(self._start(self._configuration_with(variable, value), variable, f"= {value!r}"))
        return attempts

    def _configuration_without(self, variable: str) -> dict[str, str]:
        configuration = dict(COMPLETE_CONFIGURATION)
        configuration.pop(variable, None)
        return configuration

    def _configuration_with(self, variable: str, value: str) -> dict[str, str]:
        configuration = dict(COMPLETE_CONFIGURATION)
        configuration[variable] = value
        return configuration

    def _start(self, configuration: dict[str, str], variable: str, form: str) -> StartupAttempt:
        with tempfile.TemporaryDirectory() as isolated_root:
            result = run_configuration_probe(configuration, Path(isolated_root))
        return StartupAttempt(
            variable=variable,
            form=form,
            exit_code=result.exit_code,
            stderr=result.diagnostics,
        )

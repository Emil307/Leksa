import time

from statements.configuration_startup_statements import (
    ACCESS_TOKEN_TTL,
    EMPTY_VALUE,
    NEGATIVE_VALUE,
    REFRESH_TOKEN_TTL,
    ZERO_VALUE,
    ConfigurationStartupStatements,
    StartupAttempt,
)

FRACTIONAL_VALUE = "1.5"
LAST_REPRESENTABLE_UTC_SECOND = 31556889864403199
ONE_SECOND = 1


class TokenConfigurationBootStatements(ConfigurationStartupStatements):
    def start_with_the_access_token_ttl_absent_or_empty(self) -> list[StartupAttempt]:
        return self._absent_and_invalid(ACCESS_TOKEN_TTL, [EMPTY_VALUE])

    def start_with_the_access_token_ttl_zero_or_negative(self) -> list[StartupAttempt]:
        return self._only_invalid(ACCESS_TOKEN_TTL, [ZERO_VALUE, NEGATIVE_VALUE])

    def start_with_the_access_token_ttl_fractional(self) -> list[StartupAttempt]:
        return self._only_invalid(ACCESS_TOKEN_TTL, [FRACTIONAL_VALUE])

    def start_with_the_access_token_ttl_one_second_past_the_last_utc_second(self) -> list[StartupAttempt]:
        return self._only_invalid(ACCESS_TOKEN_TTL, [self._one_second_past_the_last_utc_second()])

    def start_with_the_refresh_token_ttl_absent_or_empty(self) -> list[StartupAttempt]:
        return self._absent_and_invalid(REFRESH_TOKEN_TTL, [EMPTY_VALUE])

    def start_with_the_refresh_token_ttl_zero_or_negative(self) -> list[StartupAttempt]:
        return self._only_invalid(REFRESH_TOKEN_TTL, [ZERO_VALUE, NEGATIVE_VALUE])

    def start_with_the_refresh_token_ttl_fractional(self) -> list[StartupAttempt]:
        return self._only_invalid(REFRESH_TOKEN_TTL, [FRACTIONAL_VALUE])

    def start_with_the_refresh_token_ttl_one_second_past_the_last_utc_second(self) -> list[StartupAttempt]:
        return self._only_invalid(REFRESH_TOKEN_TTL, [self._one_second_past_the_last_utc_second()])

    def _only_invalid(self, variable: str, values: list[str]) -> list[StartupAttempt]:
        return [self._start(self._configuration_with(variable, value), variable, f"= {value!r}") for value in values]

    def _one_second_past_the_last_utc_second(self) -> str:
        return str(LAST_REPRESENTABLE_UTC_SECOND - int(time.time()) + ONE_SECOND)

from pathlib import Path

from statements.jvm_configuration_probe import ProbeResult, run_configuration_probe

SIGNING_SECRET_VARIABLE = "JWT_SECRET"
BLANK_SECRET = ""
WHITESPACE_SECRET = "   "
SUCCESSFUL_EXIT_CODE = 0


class SigningSecretBootStatements:
    def __init__(self, deployment_directory: Path):
        self.deployment_directory = deployment_directory
        self.configuration: dict[str, str] = {}
        self.attempt = ProbeResult(exit_code=SUCCESSFUL_EXIT_CODE, diagnostics="")

    def given_the_signing_secret_variable_is_absent(self) -> None:
        self.configuration = {}

    def given_the_signing_secret_is(self, value: str) -> None:
        self.configuration = {SIGNING_SECRET_VARIABLE: value}

    def when_the_application_starts(self) -> None:
        self.attempt = run_configuration_probe(self.configuration, self.deployment_directory)

    def assert_startup_failed_with_an_explicit_configuration_error(self) -> None:
        assert self.attempt.exit_code != SUCCESSFUL_EXIT_CODE, self.attempt.diagnostics
        assert SIGNING_SECRET_VARIABLE in self.attempt.diagnostics, self.attempt.diagnostics

    def assert_no_working_default_was_used(self) -> None:
        assert self.attempt.exit_code != SUCCESSFUL_EXIT_CODE, self.attempt.diagnostics

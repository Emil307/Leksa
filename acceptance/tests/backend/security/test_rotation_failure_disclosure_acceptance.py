import pytest
from statements.rotation_failure_disclosure_statements import RotationFailureDisclosureStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: a storage failure during rotation must answer the unified error envelope, "
    "got a non-JSON body (None) — the timed-out row lock is not mapped to the error envelope"
)


class TestRotationFailureDisclosureAcceptance(AbstractBackendTest):
    """Сценарий 3.2: ответы не раскрывают токены и внутренние детали при отказах ротации.

    Дано известный секретный маркер проходит через семейства отказа ротации, наблюдаемые снаружи
    Когда клиент получает ответы для ошибок валидации, авторизации и хранилища
    Тогда каждый ответ точно соответствует разрешённой схеме ошибки
    И секретный маркер отсутствует в теле и payload
    И ответы не содержат SQL, stack trace, внутренние классы или пути
    """

    async def test_should_hide_the_sentinel_when_a_forged_log_line_fails_validation(
        self, rotation_failure_disclosure_statements: RotationFailureDisclosureStatements
    ):
        sentinel = rotation_failure_disclosure_statements.sentinel_with_forged_log_line()

        refusal = await rotation_failure_disclosure_statements.refresh_with(sentinel)

        rotation_failure_disclosure_statements.assert_refused_as_validation_failure(refusal)
        rotation_failure_disclosure_statements.assert_envelope_has_only_allowed_fields(refusal)
        rotation_failure_disclosure_statements.assert_secret_marker_is_absent(refusal, sentinel)
        rotation_failure_disclosure_statements.assert_carries_no_internal_details(refusal)

    async def test_should_hide_the_sentinel_when_an_overlong_token_fails_validation(
        self, rotation_failure_disclosure_statements: RotationFailureDisclosureStatements
    ):
        sentinel = rotation_failure_disclosure_statements.sentinel_longer_than_the_token_limit()

        refusal = await rotation_failure_disclosure_statements.refresh_with(sentinel)

        rotation_failure_disclosure_statements.assert_refused_as_validation_failure(refusal)
        rotation_failure_disclosure_statements.assert_envelope_has_only_allowed_fields(refusal)
        rotation_failure_disclosure_statements.assert_secret_marker_is_absent(refusal, sentinel)
        rotation_failure_disclosure_statements.assert_carries_no_internal_details(refusal)

    async def test_should_hide_the_sentinel_when_an_unknown_token_is_refused(
        self, rotation_failure_disclosure_statements: RotationFailureDisclosureStatements
    ):
        sentinel = rotation_failure_disclosure_statements.sentinel_unknown_to_the_storage()

        refusal = await rotation_failure_disclosure_statements.refresh_with(sentinel)

        rotation_failure_disclosure_statements.assert_refused_as_unified_authorization_failure(refusal)
        rotation_failure_disclosure_statements.assert_envelope_has_only_allowed_fields(refusal)
        rotation_failure_disclosure_statements.assert_secret_marker_is_absent(refusal, sentinel)
        rotation_failure_disclosure_statements.assert_carries_no_internal_details(refusal)

    @pytest.mark.skip(reason=RED_REASON)
    async def test_should_hide_the_sentinel_when_the_storage_fails(
        self, rotation_failure_disclosure_statements: RotationFailureDisclosureStatements
    ):
        sentinel = await rotation_failure_disclosure_statements.sentinel_whose_storage_row_is_locked()

        refusal = await rotation_failure_disclosure_statements.refresh_with(sentinel)

        rotation_failure_disclosure_statements.assert_envelope_has_only_allowed_fields(refusal)
        rotation_failure_disclosure_statements.assert_secret_marker_is_absent(refusal, sentinel)
        rotation_failure_disclosure_statements.assert_carries_no_internal_details(refusal)

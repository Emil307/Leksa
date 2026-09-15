from statements.refresh_request_validation_statements import RefreshRequestValidationStatements
from statements.session_rotation_consistency_statements import SessionRotationConsistencyStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestRefreshRequestValidationAcceptance(AbstractBackendTest):
    """Сценарий 1.1: недопустимый запрос обновления отклоняется без изменения сессии.

    Дано существует действующая сессия
    Когда клиент отправляет обновление токенов с недопустимым вариантом запроса
    Тогда ответ имеет ошибку валидации
    И действующая сессия остаётся без изменений
    """

    async def test_should_reject_a_request_without_a_valid_json_body_and_keep_the_session(
        self,
        refresh_request_validation_statements: RefreshRequestValidationStatements,
        session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    ):
        live = await session_rotation_consistency_statements.given_live_session_in_real_storage()

        await refresh_request_validation_statements.send_each_and_assert_validation_error(
            refresh_request_validation_statements.requests_without_a_valid_json_body()
        )

        await refresh_request_validation_statements.assert_session_row_is_unchanged(live)
        await refresh_request_validation_statements.assert_live_refresh_token_still_rotates(live)

    async def test_should_reject_a_missing_null_or_empty_token_and_keep_the_session(
        self,
        refresh_request_validation_statements: RefreshRequestValidationStatements,
        session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    ):
        live = await session_rotation_consistency_statements.given_live_session_in_real_storage()

        await refresh_request_validation_statements.send_each_and_assert_validation_error(
            refresh_request_validation_statements.requests_with_a_missing_null_or_empty_token()
        )

        await refresh_request_validation_statements.assert_session_row_is_unchanged(live)
        await refresh_request_validation_statements.assert_live_refresh_token_still_rotates(live)

    async def test_should_reject_an_ill_formed_token_and_keep_the_session(
        self,
        refresh_request_validation_statements: RefreshRequestValidationStatements,
        session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    ):
        live = await session_rotation_consistency_statements.given_live_session_in_real_storage()

        await refresh_request_validation_statements.send_each_and_assert_validation_error(
            refresh_request_validation_statements.requests_with_an_ill_formed_token(live)
        )

        await refresh_request_validation_statements.assert_session_row_is_unchanged(live)
        await refresh_request_validation_statements.assert_live_refresh_token_still_rotates(live)

from statements.session_rotation_consistency_statements import SessionRotationConsistencyStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSessionRotationConsistencyAcceptance(AbstractBackendTest):
    """Интеграция 1.1: успешный запрос согласованно обновляет хранилище и выпускает JWT.

    Дано в реальном хранилище существует действующая сессия
    Когда клиент обновляет токены через приложение
    Тогда REST-ответ содержит прежний идентификатор сессии и новую пару
    И в той же строке хранилища совместно сохранены новый refresh-токен и новый срок
    И новый access-токен проверяется с прежними пользователем и сессией
    И старый refresh-токен больше не действует
    """

    async def test_should_rotate_storage_row_and_jwt_consistently(
        self, session_rotation_consistency_statements: SessionRotationConsistencyStatements
    ):
        live = await session_rotation_consistency_statements.given_live_session_in_real_storage()

        rotation = await session_rotation_consistency_statements.rotate_tokens_through_the_application(live)
        profile = await session_rotation_consistency_statements.request_profile_with_rotated_token(rotation)

        session_rotation_consistency_statements.assert_rotation_answered_with_same_session_and_new_pair(live, rotation)
        session_rotation_consistency_statements.assert_same_row_stores_new_token_and_new_expiry(live, rotation)
        session_rotation_consistency_statements.assert_no_other_session_row_was_opened(live, rotation)
        session_rotation_consistency_statements.assert_new_access_token_verifies_with_previous_user_and_session(
            live, rotation
        )
        session_rotation_consistency_statements.assert_profile_of_rotated_session_returned(profile, live)

    async def test_should_refuse_old_refresh_token_without_touching_the_row(
        self, session_rotation_consistency_statements: SessionRotationConsistencyStatements
    ):
        live = await session_rotation_consistency_statements.given_rotated_live_session()

        retry = await session_rotation_consistency_statements.retry_with_old_refresh_token(live)

        session_rotation_consistency_statements.assert_retry_is_refused_with_unified_envelope(retry)
        session_rotation_consistency_statements.assert_stored_row_is_unchanged_by_the_retry(retry)

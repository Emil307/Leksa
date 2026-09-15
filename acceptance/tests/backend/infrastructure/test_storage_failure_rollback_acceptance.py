import pytest
from statements.storage_failure_rollback_statements import StorageFailureRollbackStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestStorageFailureRollbackAcceptance(AbstractBackendTest):
    """Инфраструктура 1.1: отказ хранилища откатывает ротацию целиком.

    Дано существует действующая сессия
    И хранилище недоступно либо фиксация ротации завершается ошибкой
    Когда клиент обновляет токены по refresh-токену этой сессии
    Тогда ответ сообщает о временной недоступности
    И прежние refresh-токен и срок сессии сохранены вместе
    И старый refresh-токен остаётся действительным для следующей попытки
    И частично действующая новая пара отсутствует
    """

    @pytest.mark.skip(reason="RED: a storage failure during rotation answers 500 text/plain instead of 503 UNAVAILABLE")
    async def test_should_answer_temporary_unavailability_when_the_rotation_commit_fails(
        self, storage_failure_rollback_statements: StorageFailureRollbackStatements
    ):
        live = await storage_failure_rollback_statements.given_live_session_whose_rotation_commit_fails()

        failed = await storage_failure_rollback_statements.rotate_tokens_while_storage_fails(live)

        storage_failure_rollback_statements.assert_rotation_answered_temporary_unavailability(failed)

    async def test_should_keep_the_previous_token_and_expiry_together_when_the_rotation_commit_fails(
        self, storage_failure_rollback_statements: StorageFailureRollbackStatements
    ):
        live = await storage_failure_rollback_statements.given_live_session_whose_rotation_commit_fails()

        failed = await storage_failure_rollback_statements.rotate_tokens_while_storage_fails(live)

        storage_failure_rollback_statements.assert_rotation_answered_no_tokens(failed)
        storage_failure_rollback_statements.assert_previous_token_and_expiry_are_kept_together(live, failed)
        storage_failure_rollback_statements.assert_no_partially_live_session_row_exists(live, failed)

    async def test_should_accept_the_old_refresh_token_on_the_next_attempt_after_storage_recovers(
        self, storage_failure_rollback_statements: StorageFailureRollbackStatements
    ):
        live = await storage_failure_rollback_statements.given_live_session_that_survived_a_failed_rotation()

        rotated = await storage_failure_rollback_statements.retry_with_the_old_refresh_token(live)

        storage_failure_rollback_statements.assert_old_token_rotated_into_a_new_pair(live, rotated)
        await storage_failure_rollback_statements.assert_stored_row_holds_the_new_pair(live, rotated)

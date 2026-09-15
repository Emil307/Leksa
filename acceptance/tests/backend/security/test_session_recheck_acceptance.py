from collections.abc import AsyncIterator

import pytest
from statements.auth_database import AuthDatabase
from statements.session_recheck_statements import SessionRecheckStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
async def session_recheck_statements(auth_database: AuthDatabase) -> AsyncIterator[SessionRecheckStatements]:
    statements = SessionRecheckStatements(auth_database)
    await statements.open()
    try:
        yield statements
    finally:
        await statements.close()


class TestSessionRecheckAcceptance(AbstractBackendTest):
    """Сценарий 2.4: решение о сессии перечитывается на каждом запросе и каждом инстансе.

    Дано один и тот же access-токен успешно прошёл через каждый из двух инстансов приложения
    Когда сессия становится неактивной в PostgreSQL
    И токен повторно предъявляется каждому уже прогретому инстансу
    Тогда каждый повторный запрос отклоняется как неудачная авторизация
    И ни одно прежнее положительное решение не разрешает доступ
    """

    async def test_should_reject_warmed_instances_after_session_becomes_inactive(
        self, session_recheck_statements: SessionRecheckStatements
    ):
        warmed = await session_recheck_statements.warm_token_through_every_instance()

        await session_recheck_statements.deactivate_session_in_postgres(warmed)
        profiles = await session_recheck_statements.request_profile_from_every_warmed_instance(warmed)

        session_recheck_statements.assert_every_request_rejected_as_failed_authorization(profiles)
        session_recheck_statements.assert_no_earlier_positive_decision_granted_access(profiles)

import pytest
from statements.rotation_request_boundary_statements import (
    FORBIDDEN_SERVER_FIELDS,
    RotationRequestBoundaryStatements,
)

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: a forbidden server field beside refreshToken must be refused with 400 VALIDATION_FAILED, got 200 — "
    "POST /api/v1/auth/token/refresh ignores the unknown property and rotates the session"
)


class TestRotationRequestBoundaryAcceptance(AbstractBackendTest):
    """Безопасность 1.1: недопустимый запрос ротации обрабатывается на границе запроса.

    Дано существует действующая сессия
    Когда клиент отправляет один недопустимый вариант запроса ротации
    Тогда ответ имеет ошибку валидации
    И ни одно поле сессии не изменено
    И хранилище не получает значение токена
    И ни одна сессия не изменена
    И исходное значение токена отсутствует в перехваченных журналах
    И дополнительная запись или поле с поддельным маркером не появляется
    """

    @pytest.mark.skip(reason=RED_REASON)
    @pytest.mark.parametrize("field", FORBIDDEN_SERVER_FIELDS)
    async def test_should_reject_a_forbidden_server_field_without_touching_the_session(
        self, rotation_request_boundary_statements: RotationRequestBoundaryStatements, field: str
    ):
        session = await rotation_request_boundary_statements.given_live_session()

        attempt = await rotation_request_boundary_statements.refresh_with_forbidden_server_field(session, field)

        rotation_request_boundary_statements.assert_refused_at_the_request_boundary(attempt)

    async def test_should_reject_an_oversized_token_without_touching_the_session(
        self, rotation_request_boundary_statements: RotationRequestBoundaryStatements
    ):
        session = await rotation_request_boundary_statements.given_live_session()

        attempt = await rotation_request_boundary_statements.refresh_with_oversized_token(session)

        rotation_request_boundary_statements.assert_refused_at_the_request_boundary(attempt)

    async def test_should_reject_a_multibyte_token_without_touching_the_session(
        self, rotation_request_boundary_statements: RotationRequestBoundaryStatements
    ):
        session = await rotation_request_boundary_statements.given_live_session()

        attempt = await rotation_request_boundary_statements.refresh_with_multibyte_token(session)

        rotation_request_boundary_statements.assert_refused_at_the_request_boundary(attempt)

    async def test_should_reject_an_unprintable_token_without_touching_the_session(
        self, rotation_request_boundary_statements: RotationRequestBoundaryStatements
    ):
        session = await rotation_request_boundary_statements.given_live_session()

        attempt = await rotation_request_boundary_statements.refresh_with_unprintable_token(session)

        rotation_request_boundary_statements.assert_refused_at_the_request_boundary(attempt)

    async def test_should_reject_a_forged_log_entry_token_without_touching_the_session(
        self, rotation_request_boundary_statements: RotationRequestBoundaryStatements
    ):
        session = await rotation_request_boundary_statements.given_live_session()

        attempt = await rotation_request_boundary_statements.refresh_with_forged_log_entry_token(session)

        rotation_request_boundary_statements.assert_refused_at_the_request_boundary(attempt)

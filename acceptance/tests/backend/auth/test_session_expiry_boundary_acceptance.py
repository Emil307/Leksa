from statements.session_expiry_boundary_statements import SessionExpiryBoundaryStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSessionExpiryBoundaryAcceptance(AbstractBackendTest):
    """API 3.2: срок сессии имеет строгую границу истечения.

    Дано время управляется относительно срока действующей сессии
    Когда клиент обновляет токены непосредственно до срока, ровно в срок и сразу после срока
    Тогда запрос до срока успешен
    И запросы в срок и после срока имеют единую ошибку авторизации
    И отклонённые запросы не меняют токен и срок сессии
    И отклонённые запросы не выпускают действующую пару
    """

    async def test_should_rotate_tokens_just_before_the_deadline(
        self, session_expiry_boundary_statements: SessionExpiryBoundaryStatements
    ):
        subject = await session_expiry_boundary_statements.given_session_expiring_just_after_the_request()

        rotation = await session_expiry_boundary_statements.rotate_tokens(subject)

        session_expiry_boundary_statements.assert_rotation_succeeded_for_the_same_session(subject, rotation)

    async def test_should_refuse_rotation_exactly_at_the_deadline(
        self, session_expiry_boundary_statements: SessionExpiryBoundaryStatements
    ):
        subject = await session_expiry_boundary_statements.given_session_expiring_at_this_very_moment()

        refused = await session_expiry_boundary_statements.rotate_tokens_capturing_refusal(subject)

        session_expiry_boundary_statements.assert_refused_with_unified_authorization_error(refused)
        session_expiry_boundary_statements.assert_session_token_and_deadline_are_untouched(subject, refused)
        session_expiry_boundary_statements.assert_no_token_pair_was_issued(refused)

    async def test_should_refuse_rotation_just_after_the_deadline(
        self, session_expiry_boundary_statements: SessionExpiryBoundaryStatements
    ):
        subject = await session_expiry_boundary_statements.given_session_expired_a_microsecond_ago()

        refused = await session_expiry_boundary_statements.rotate_tokens_capturing_refusal(subject)

        session_expiry_boundary_statements.assert_refused_with_unified_authorization_error(refused)
        session_expiry_boundary_statements.assert_session_token_and_deadline_are_untouched(subject, refused)
        session_expiry_boundary_statements.assert_no_token_pair_was_issued(refused)

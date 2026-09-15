from statements.indistinguishable_refresh_refusal_statements import IndistinguishableRefreshRefusalStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestIndistinguishableRefreshRefusalAcceptance(AbstractBackendTest):
    """Сценарий 3.1: недействительные refresh-токены неразличимы снаружи.

    Дано подготовлены истёкший, неизвестный и уже использованный refresh-токены
    Когда клиент по очереди запрашивает обновление с каждым токеном
    Тогда каждый ответ имеет одну и ту же ошибку авторизации
    И статус, код, сообщение и payload всех ответов побайтно совпадают
    И ни одна сессия не изменена
    И ни один запрос не выпускает действующую пару
    """

    async def test_should_refuse_every_invalid_token_with_byte_identical_envelope(
        self, indistinguishable_refresh_refusal_statements: IndistinguishableRefreshRefusalStatements
    ):
        tokens = await indistinguishable_refresh_refusal_statements.given_expired_unknown_and_used_refresh_tokens()

        round_ = await indistinguishable_refresh_refusal_statements.request_refresh_with_each_token_in_turn(tokens)

        indistinguishable_refresh_refusal_statements.assert_every_refusal_is_the_unified_authorization_refusal(round_)
        indistinguishable_refresh_refusal_statements.assert_status_and_envelope_bytes_are_identical(round_)

    async def test_should_leave_sessions_untouched_and_issue_no_pair(
        self, indistinguishable_refresh_refusal_statements: IndistinguishableRefreshRefusalStatements
    ):
        tokens = await indistinguishable_refresh_refusal_statements.given_expired_unknown_and_used_refresh_tokens()

        round_ = await indistinguishable_refresh_refusal_statements.request_refresh_with_each_token_in_turn(tokens)

        indistinguishable_refresh_refusal_statements.assert_no_session_was_changed(tokens, round_)
        indistinguishable_refresh_refusal_statements.assert_no_refusal_issued_a_token_pair(round_)

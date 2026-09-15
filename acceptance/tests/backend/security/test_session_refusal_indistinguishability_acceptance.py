from statements.session_refusal_indistinguishability_statements import SessionRefusalIndistinguishabilityStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSessionRefusalIndistinguishabilityAcceptance(AbstractBackendTest):
    """Безопасность 2.2: недоступная и отсутствующая сессии неразличимы снаружи.

    Дано подготовлены недоступный клиенту и отсутствующий refresh-токены
    Когда клиент запрашивает обновление с каждым токеном
    Тогда ответы имеют одинаковые статус, код, сообщение и payload
    И ответы не раскрывают владельца или существование сессии
    И ни одна сессия не изменена
    """

    async def test_should_refuse_expired_and_absent_tokens_identically(
        self, session_refusal_indistinguishability_statements: SessionRefusalIndistinguishabilityStatements
    ):
        prepared = await session_refusal_indistinguishability_statements.given_expired_session_and_absent_token()

        pair = await session_refusal_indistinguishability_statements.refresh_with_each_token(prepared)

        session_refusal_indistinguishability_statements.assert_both_refusals_are_the_unified_authorization_refusal(pair)
        session_refusal_indistinguishability_statements.assert_refusals_are_identical(pair)
        session_refusal_indistinguishability_statements.assert_refusals_reveal_neither_owner_nor_existence(
            prepared, pair
        )
        session_refusal_indistinguishability_statements.assert_no_session_was_changed(prepared, pair)

    async def test_should_refuse_used_and_absent_tokens_identically(
        self, session_refusal_indistinguishability_statements: SessionRefusalIndistinguishabilityStatements
    ):
        prepared = await session_refusal_indistinguishability_statements.given_used_token_and_absent_token()

        pair = await session_refusal_indistinguishability_statements.refresh_with_each_token(prepared)

        session_refusal_indistinguishability_statements.assert_both_refusals_are_the_unified_authorization_refusal(pair)
        session_refusal_indistinguishability_statements.assert_refusals_are_identical(pair)
        session_refusal_indistinguishability_statements.assert_refusals_reveal_neither_owner_nor_existence(
            prepared, pair
        )
        session_refusal_indistinguishability_statements.assert_no_session_was_changed(prepared, pair)

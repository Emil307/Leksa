from statements.lost_rotation_response_statements import LostRotationResponseStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestLostRotationResponseAcceptance(AbstractBackendTest):
    """Интеграция 1.3: потерянный успешный ответ не допускает второй ротации.

    Дано успешная ротация зафиксирована, но её ответ потерян
    Когда клиент повторяет запрос со старым refresh-токеном
    Тогда повтор имеет единую ошибку авторизации
    И в хранилище присутствует ровно одна полная ротация
    И новая пара первого запроса остаётся действительной
    И повтор не отзывает и не заменяет эту пару
    """

    async def test_should_refuse_the_replayed_old_token_with_the_unified_error(
        self, lost_rotation_response_statements: LostRotationResponseStatements
    ):
        lost = await lost_rotation_response_statements.given_committed_rotation_whose_response_was_lost()

        replay = await lost_rotation_response_statements.replay_with_old_refresh_token(lost)

        lost_rotation_response_statements.assert_replay_is_refused_with_unified_error(replay)

    async def test_should_keep_exactly_one_full_rotation_without_replacing_the_pair(
        self, lost_rotation_response_statements: LostRotationResponseStatements
    ):
        lost = await lost_rotation_response_statements.given_committed_rotation_whose_response_was_lost()

        replay = await lost_rotation_response_statements.replay_with_old_refresh_token(lost)

        lost_rotation_response_statements.assert_storage_holds_exactly_the_committed_rotation(lost, replay)
        lost_rotation_response_statements.assert_replay_did_not_replace_the_lost_pair(lost, replay)

    async def test_should_keep_the_lost_pair_valid_after_the_replay(
        self, lost_rotation_response_statements: LostRotationResponseStatements
    ):
        lost = await lost_rotation_response_statements.given_committed_rotation_whose_response_was_lost()
        await lost_rotation_response_statements.replay_with_old_refresh_token(lost)

        usage = await lost_rotation_response_statements.use_the_lost_pair_after_the_replay(lost)

        lost_rotation_response_statements.assert_lost_access_token_still_opens_the_profile(lost, usage)
        lost_rotation_response_statements.assert_lost_refresh_token_still_rotates_the_same_session(lost, usage)

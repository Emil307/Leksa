from statements.concurrent_rotation_statements import ConcurrentRotationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestConcurrentRotationAcceptance(AbstractBackendTest):
    """Сценарий 3.3: один refresh-токен выигрывает только одну конкурентную ротацию.

    Дано два независимых запроса остановлены на одной точке ротации действующей сессии
    Когда оба запроса продолжают обновление с одним refresh-токеном
    Тогда ровно один ответ успешен
    И второй ответ имеет единую ошибку авторизации
    И в сессии зафиксирована ровно одна полная ротация
    И новая пара победившего запроса остаётся действительной
    """

    async def test_should_answer_exactly_one_of_two_simultaneous_rotations_successfully(
        self, concurrent_rotation_statements: ConcurrentRotationStatements
    ):
        live = await concurrent_rotation_statements.given_live_session_in_real_storage()

        race = await concurrent_rotation_statements.release_two_rotations_with_the_same_token_together(live)

        concurrent_rotation_statements.assert_exactly_one_answer_is_successful(live, race)
        concurrent_rotation_statements.assert_the_other_answer_is_the_unified_authorization_refusal(race)

    async def test_should_store_exactly_one_full_rotation_of_the_session(
        self, concurrent_rotation_statements: ConcurrentRotationStatements
    ):
        live = await concurrent_rotation_statements.given_live_session_in_real_storage()

        race = await concurrent_rotation_statements.release_two_rotations_with_the_same_token_together(live)

        concurrent_rotation_statements.assert_exactly_one_answer_is_successful(live, race)
        concurrent_rotation_statements.assert_exactly_one_full_rotation_is_stored(live, race)

    async def test_should_keep_the_winning_pair_valid(
        self, concurrent_rotation_statements: ConcurrentRotationStatements
    ):
        live = await concurrent_rotation_statements.given_live_session_in_real_storage()
        race = await concurrent_rotation_statements.release_two_rotations_with_the_same_token_together(live)
        concurrent_rotation_statements.assert_exactly_one_answer_is_successful(live, race)

        profile = await concurrent_rotation_statements.request_profile_with_the_winning_access_token(race)
        rotated = await concurrent_rotation_statements.rotate_again_with_the_winning_refresh_token(race)

        concurrent_rotation_statements.assert_winning_access_token_verifies_with_previous_user_and_session(live, race)
        concurrent_rotation_statements.assert_profile_of_the_winning_session_returned(profile, live)
        concurrent_rotation_statements.assert_winning_refresh_token_rotated_the_same_session(live, race, rotated)

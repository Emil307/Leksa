import pytest
from clients.application.profile_client import ProfileClient
from statements.profile_owner_selection_statements import ProfileOwnerSelectionStatements
from statements.profile_statements import ProfileStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def profile_owner_selection_statements(
    profile_client: ProfileClient,
    profile_statements: ProfileStatements,
) -> ProfileOwnerSelectionStatements:
    return ProfileOwnerSelectionStatements(profile_client, profile_statements)


class TestProfileOwnerSelectionAcceptance(AbstractBackendTest):
    """Сценарий 3.1: клиентское значение userId не может выбрать чужой профиль.

    Дано два пользователя имеют разные учётные записи и действующие сессии
    И первый пользователь предъявляет свой корректный access-токен
    Когда первый пользователь запрашивает профиль и передаёт идентификатор второго
    Тогда запрос успешно выполнен
    И ответ содержит только учётную запись первого пользователя
    И данные второго пользователя не возвращаются
    """

    async def test_should_ignore_client_sent_user_id_and_answer_with_the_token_owner(
        self, profile_owner_selection_statements: ProfileOwnerSelectionStatements
    ):
        requester, other = await profile_owner_selection_statements.sign_in_two_users_with_separate_accounts()

        profile = await profile_owner_selection_statements.request_own_profile_passing_other_user_identifier(
            requester, other
        )

        profile_owner_selection_statements.assert_request_succeeded(profile)
        profile_owner_selection_statements.assert_carries_only_requesters_account(profile, requester)
        profile_owner_selection_statements.assert_other_users_data_is_absent(profile, other)

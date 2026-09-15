from statements.profile_statements import ProfileStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestProfileReadAcceptance(AbstractBackendTest):
    """Сценарий 1.1: пользователь с действующей сессией получает всю свою запись.

    Дано пользователь имеет действующую сессию и корректный access-токен
    И в его учётной записи заполнено каждое поле
    Когда пользователь запрашивает свой профиль
    Тогда запрос успешно выполнен
    И ответ содержит все поля его учётной записи в клиентских именах
    И значения ответа точно совпадают с сохранённой записью
    И ответ не обёрнут во внешний конверт
    И в ответе нет данных сессии, токенов и учебного профиля
    """

    async def test_should_return_every_stored_account_field_in_client_names(
        self, profile_statements: ProfileStatements
    ):
        user = await profile_statements.sign_in_user_with_every_field_filled()

        profile = await profile_statements.request_own_profile(user)

        profile_statements.assert_request_succeeded(profile)
        profile_statements.assert_carries_every_client_field_name(profile)
        profile_statements.assert_values_match_stored_record(profile, user)
        profile_statements.assert_response_is_not_wrapped_in_envelope(profile)
        profile_statements.assert_response_carries_no_session_token_or_learner_data(profile)

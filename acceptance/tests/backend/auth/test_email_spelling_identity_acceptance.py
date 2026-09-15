from statements.email_spelling_identity_statements import EmailSpellingIdentityStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestEmailSpellingIdentityAcceptance(AbstractBackendTest):
    """Сценарий 8.4: регистр и форма записи email — одна личность.

    Дано пользователь запросил код на email в написании <написание>
    Когда пользователь запрашивает код на тот же адрес в другом написании, не дожидаясь конца кулдауна
    Тогда второй запрос отклоняется по кулдауну
    И вход по коду из первой заявки создаёт ровно одного пользователя
    И повторный вход в любом написании возвращает того же пользователя

    Написание: разный регистр (`User@Example.COM` и `user@example.com`); разные формы
    нормализации Юникода (NFC и NFD); под турецкой локалью, где заглавная `I` в нижнем
    регистре даёт `ı`.
    """

    async def test_should_keep_one_identity_across_letter_case(
        self, email_spelling_identity_statements: EmailSpellingIdentityStatements
    ):
        pair, requested = await email_spelling_identity_statements.given_code_requested_in_another_case()

        denial = await email_spelling_identity_statements.request_code_in_the_other_spelling(pair)

        email_spelling_identity_statements.assert_rejected_by_cooldown(denial)
        first = await email_spelling_identity_statements.log_in_with_the_first_code(requested)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(first, pair)
        second = await email_spelling_identity_statements.log_in_again_in_the_other_spelling(pair)
        email_spelling_identity_statements.assert_the_same_user_came_back(first, second, pair)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(second, pair)

    async def test_should_keep_one_identity_across_unicode_normalization_forms(
        self, email_spelling_identity_statements: EmailSpellingIdentityStatements
    ):
        pair, requested = await email_spelling_identity_statements.given_code_requested_in_decomposed_form()

        denial = await email_spelling_identity_statements.request_code_in_the_other_spelling(pair)

        email_spelling_identity_statements.assert_rejected_by_cooldown(denial)
        first = await email_spelling_identity_statements.log_in_with_the_first_code(requested)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(first, pair)
        second = await email_spelling_identity_statements.log_in_again_in_the_other_spelling(pair)
        email_spelling_identity_statements.assert_the_same_user_came_back(first, second, pair)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(second, pair)

    async def test_should_keep_one_identity_for_a_capital_dotted_i(
        self, email_spelling_identity_statements: EmailSpellingIdentityStatements
    ):
        pair, requested = await email_spelling_identity_statements.given_code_requested_with_a_capital_dotted_i()

        denial = await email_spelling_identity_statements.request_code_in_the_other_spelling(pair)

        email_spelling_identity_statements.assert_rejected_by_cooldown(denial)
        first = await email_spelling_identity_statements.log_in_with_the_first_code(requested)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(first, pair)
        second = await email_spelling_identity_statements.log_in_again_in_the_other_spelling(pair)
        email_spelling_identity_statements.assert_the_same_user_came_back(first, second, pair)
        await email_spelling_identity_statements.assert_exactly_one_user_owns_the_address(second, pair)

from typing import Any

import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.jwt_claims_statements import (
    NON_INTEGER_EXPIRIES,
    NON_STRING_AUDIENCES,
    NON_UUID_IDENTIFIERS,
    REQUIRED_CLAIMS,
    WRONG_AUDIENCES,
    JwtClaimsStatements,
)

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def jwt_claims_statements(profile_client: ProfileClient, auth_database: AuthDatabase) -> JwtClaimsStatements:
    return JwtClaimsStatements(profile_client, auth_database)


class TestJwtClaimsAcceptance(AbstractBackendTest):
    """Сценарий 2.2: каждый обязательный claim проверяется без неявных преобразований.

    Дано существует пользователь с действующей сессией
    Когда клиент запрашивает профиль с вариантом claims <вариант>
    Тогда запрос отклоняется как неудачная авторизация
    И ответ дословно совпадает с единым отказом авторизации
    И значение не приводится к другому типу молча
    """

    @pytest.mark.parametrize("claim", REQUIRED_CLAIMS)
    async def test_should_reject_token_missing_a_required_claim(
        self, jwt_claims_statements: JwtClaimsStatements, claim: str
    ):
        session = await jwt_claims_statements.sign_in_user()

        outcome = await jwt_claims_statements.request_profile_without_claim(session, claim)

        jwt_claims_statements.assert_matches_unified_authorization_refusal(outcome)
        jwt_claims_statements.assert_no_value_was_silently_coerced(outcome)

    @pytest.mark.parametrize(("claim", "value"), NON_UUID_IDENTIFIERS)
    async def test_should_reject_identifier_claim_that_is_not_a_uuid_string(
        self, jwt_claims_statements: JwtClaimsStatements, claim: str, value: Any
    ):
        session = await jwt_claims_statements.sign_in_user()

        outcome = await jwt_claims_statements.request_profile_with_claim_value(session, claim, value)

        jwt_claims_statements.assert_matches_unified_authorization_refusal(outcome)
        jwt_claims_statements.assert_no_value_was_silently_coerced(outcome)

    @pytest.mark.parametrize("value", NON_INTEGER_EXPIRIES)
    async def test_should_reject_expiry_that_is_not_an_integer(
        self, jwt_claims_statements: JwtClaimsStatements, value: Any
    ):
        session = await jwt_claims_statements.sign_in_user()

        outcome = await jwt_claims_statements.request_profile_with_expiry(session, value)

        jwt_claims_statements.assert_matches_unified_authorization_refusal(outcome)
        jwt_claims_statements.assert_no_value_was_silently_coerced(outcome)

    @pytest.mark.parametrize("value", NON_STRING_AUDIENCES)
    async def test_should_reject_audience_that_is_not_a_string(
        self, jwt_claims_statements: JwtClaimsStatements, value: Any
    ):
        session = await jwt_claims_statements.sign_in_user()

        outcome = await jwt_claims_statements.request_profile_with_audience(session, value)

        jwt_claims_statements.assert_matches_unified_authorization_refusal(outcome)
        jwt_claims_statements.assert_no_value_was_silently_coerced(outcome)

    @pytest.mark.parametrize("value", WRONG_AUDIENCES)
    async def test_should_reject_audience_differing_in_case_or_value(
        self, jwt_claims_statements: JwtClaimsStatements, value: str
    ):
        session = await jwt_claims_statements.sign_in_user()

        outcome = await jwt_claims_statements.request_profile_with_audience(session, value)

        jwt_claims_statements.assert_matches_unified_authorization_refusal(outcome)
        jwt_claims_statements.assert_no_value_was_silently_coerced(outcome)

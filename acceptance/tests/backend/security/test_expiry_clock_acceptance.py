import pytest
from clients.application.profile_client import ProfileClient
from httpx import AsyncClient
from statements.auth_database import AuthDatabase
from statements.expiry_clock_statements import ExpiryClockStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def expiry_clock_statements(http_client: AsyncClient, auth_database: AuthDatabase) -> ExpiryClockStatements:
    return ExpiryClockStatements(ProfileClient(http_client), auth_database)


class TestExpiryClockAcceptance(AbstractBackendTest):
    """Сценарий 2.3: обе границы истечения используют одни управляемые часы.

    Дано пользователь имеет корректный access-токен и связанную с ним сессию
    Когда срок <граница> имеет случай <случай>
    Тогда запрос имеет исход <исход>
    """

    async def test_should_return_profile_a_second_before_the_token_expires(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_token_is_moments_from_expiry()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_profile_returned(profile, subject)

    async def test_should_refuse_a_token_that_expires_at_this_very_second(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_token_expires_at_this_very_second()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_token_that_expired_a_second_ago(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_token_expired_a_second_ago()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_token_whose_expiry_is_zero(self, expiry_clock_statements: ExpiryClockStatements):
        subject = await expiry_clock_statements.user_whose_token_expiry_is_zero()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_token_whose_expiry_is_negative(self, expiry_clock_statements: ExpiryClockStatements):
        subject = await expiry_clock_statements.user_whose_token_expiry_is_negative()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_token_whose_expiry_reaches_the_calendar_ceiling(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_token_expiry_reaches_the_calendar_ceiling()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_token_whose_expiry_exceeds_the_exact_integer_range(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_token_expiry_exceeds_the_exact_integer_range()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_return_profile_while_the_session_still_outlives_the_request(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_session_outlives_the_request_by_a_microsecond()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_profile_returned(profile, subject)

    async def test_should_refuse_a_session_that_expires_at_this_very_moment(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_session_expires_at_this_very_moment()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

    async def test_should_refuse_a_session_that_expired_a_microsecond_ago(
        self, expiry_clock_statements: ExpiryClockStatements
    ):
        subject = await expiry_clock_statements.user_whose_session_expired_a_microsecond_ago()

        profile = await expiry_clock_statements.request_profile(subject)

        expiry_clock_statements.assert_uniform_authorization_refusal(profile)

from statements.cooldown_boundary_statements import CooldownBoundaryStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

TWO_AND_A_HALF_SECONDS_LEFT = 2500
LESS_THAN_A_SECOND_LEFT = 900
ROUNDED_UP_TO_THREE = 3
NEVER_ZERO = 1
A_TENTH_OF_A_SECOND = 0.1


class TestCooldownBoundaryAcceptance(AbstractBackendTest):
    """Сценарий 8.2: остаток кулдауна отдаётся целыми секундами на всех границах.

    Дано пользователь только что запросил код
    Когда клиент запрашивает код повторно в момент <момент>
    Тогда результат — <результат>

    За 2,5 секунды до конца — отказ по кулдауну с остатком ровно 3 (округление вверх).
    Меньше чем за секунду до конца — отказ по кулдауну с остатком ровно 1, никогда 0.
    Ровно в конце кулдауна — запрос принимается.
    Через 0,1 секунды после конца — запрос принимается.
    """

    async def test_should_round_the_remaining_wait_up_two_and_a_half_seconds_before_the_end(
        self, cooldown_boundary_statements: CooldownBoundaryStatements
    ):
        email = await cooldown_boundary_statements.given_user_just_requested_a_code()
        await cooldown_boundary_statements.given_cooldown_has_milliseconds_left(email, TWO_AND_A_HALF_SECONDS_LEFT)

        denial = await cooldown_boundary_statements.request_code_again(email)

        cooldown_boundary_statements.assert_rejected_by_cooldown_with_remaining_wait(denial, ROUNDED_UP_TO_THREE)

    async def test_should_report_one_second_never_zero_less_than_a_second_before_the_end(
        self, cooldown_boundary_statements: CooldownBoundaryStatements
    ):
        email = await cooldown_boundary_statements.given_user_just_requested_a_code()
        await cooldown_boundary_statements.given_cooldown_has_milliseconds_left(email, LESS_THAN_A_SECOND_LEFT)

        denial = await cooldown_boundary_statements.request_code_again(email)

        cooldown_boundary_statements.assert_rejected_by_cooldown_with_remaining_wait(denial, NEVER_ZERO)

    async def test_should_accept_the_request_exactly_at_the_end_of_the_cooldown(
        self, cooldown_boundary_statements: CooldownBoundaryStatements
    ):
        email = await cooldown_boundary_statements.given_user_just_requested_a_code()
        await cooldown_boundary_statements.given_cooldown_has_just_ended(email)
        await cooldown_boundary_statements.assert_cooldown_has_lapsed(email)

        challenge = await cooldown_boundary_statements.request_code_again_expecting_acceptance(email)

        cooldown_boundary_statements.assert_request_accepted(challenge)

    async def test_should_accept_the_request_a_tenth_of_a_second_after_the_end_of_the_cooldown(
        self, cooldown_boundary_statements: CooldownBoundaryStatements
    ):
        email = await cooldown_boundary_statements.given_user_just_requested_a_code()
        await cooldown_boundary_statements.given_a_moment_has_passed_since_the_cooldown_ended(
            email, A_TENTH_OF_A_SECOND
        )
        await cooldown_boundary_statements.assert_cooldown_has_lapsed(email)

        challenge = await cooldown_boundary_statements.request_code_again_expecting_acceptance(email)

        cooldown_boundary_statements.assert_request_accepted(challenge)

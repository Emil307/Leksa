from statements.concurrent_code_requests_statements import ConcurrentCodeRequestsStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestConcurrentCodeRequestsAcceptance(AbstractBackendTest):
    """Сценарий 7.1: два одновременных запроса кода дают одну заявку и один живой challenge.

    Дано в системе нет живого challenge для этого email
    Когда два запроса кода на один email доведены до управляемой точки синхронизации
    внутри захвата кулдауна и отпущены вместе
    Тогда ровно один из них создаёт challenge
    И проигравший получает отказ по кулдауну, потому что захват кулдауна условный,
    а не «прочитал и записал»
    И в очередь попадает ровно одна заявка
    """

    async def test_should_let_exactly_one_simultaneous_request_create_the_challenge(
        self, concurrent_code_requests_statements: ConcurrentCodeRequestsStatements
    ):
        email = concurrent_code_requests_statements.given_no_live_challenge_for_this_email()

        race = await concurrent_code_requests_statements.release_two_code_requests_together(email)

        concurrent_code_requests_statements.assert_exactly_one_created_a_challenge(race)
        concurrent_code_requests_statements.assert_loser_refused_by_cooldown(race)
        await concurrent_code_requests_statements.assert_single_queued_request(email)
        await concurrent_code_requests_statements.assert_winner_holds_the_only_live_challenge(race, email)

from statements.neighbor_session_isolation_statements import NeighborSessionIsolationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestNeighborSessionIsolationAcceptance(AbstractBackendTest):
    """Сценарий 2.3: ротация не затрагивает соседние сессии.

    Дано рядом существуют другая сессия этого пользователя и сессия другого пользователя
    Когда клиент обновляет токены первой сессии
    Тогда первая сессия получает новую пару и новый срок
    И обе соседние сессии остаются без изменений
    """

    async def test_should_rotate_only_the_first_session_and_leave_its_neighbors_untouched(
        self, neighbor_session_isolation_statements: NeighborSessionIsolationStatements
    ):
        neighborhood = await neighbor_session_isolation_statements.given_first_session_beside_two_neighbors()

        rotation = await neighbor_session_isolation_statements.rotate_the_first_session(neighborhood)

        neighbor_session_isolation_statements.assert_first_session_received_a_new_pair_and_a_new_expiry(
            neighborhood, rotation
        )
        neighbor_session_isolation_statements.assert_both_neighbor_sessions_are_unchanged(neighborhood, rotation)

from statements.ttl_fraction_statements import TtlFractionStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestTtlFractionAcceptance(AbstractBackendTest):
    """Инфраструктура 2.3: дробная доля времени не меняет единицы TTL.

    Дано время ротации приходится на половину секунды и сроки заданы конфигурацией в секундах
    Когда клиент успешно обновляет токены
    Тогда срок сессии равен целой секунде времени ротации плюс настроенный срок
    И срок access-токена равен той же целой секунде плюс настроенный срок, оба срока отбрасывают долю одинаково
    И ни один срок не умножен и не разделён на тысячу
    """

    async def test_session_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(
        self, ttl_fraction_statements: TtlFractionStatements
    ):
        session = await ttl_fraction_statements.given_live_session()

        rotation = await ttl_fraction_statements.rotate_at_the_half_of_a_second(session)

        ttl_fraction_statements.assert_session_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(rotation)
        ttl_fraction_statements.assert_both_deadlines_drop_the_fraction_of_the_same_second(rotation)

    async def test_access_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(
        self, ttl_fraction_statements: TtlFractionStatements
    ):
        session = await ttl_fraction_statements.given_live_session()

        rotation = await ttl_fraction_statements.rotate_at_the_half_of_a_second(session)

        ttl_fraction_statements.assert_access_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(rotation)

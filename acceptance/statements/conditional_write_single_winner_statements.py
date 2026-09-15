from statements.concurrent_rotation_statements import ConcurrentRotationStatements, RotationRace
from statements.session_rotation_consistency_statements import LiveStoredSession


class ConditionalWriteSingleWinnerStatements:
    def __init__(self, concurrent_rotation_statements: ConcurrentRotationStatements):
        self.concurrent_rotation_statements = concurrent_rotation_statements

    async def given_live_session_presented_by_two_operations(self) -> LiveStoredSession:
        return await self.concurrent_rotation_statements.given_live_session_in_real_storage()

    async def release_both_conditional_updates_together(self, live: LiveStoredSession) -> RotationRace:
        return await self.concurrent_rotation_statements.release_two_rotations_with_the_same_token_together(live)

    def assert_exactly_one_operation_changed_one_row(self, race: RotationRace) -> None:
        self.concurrent_rotation_statements.assert_exactly_one_answer_is_successful(race.live, race)

    def assert_the_other_operation_changed_no_row(self, race: RotationRace) -> None:
        self.concurrent_rotation_statements.assert_the_other_answer_is_the_unified_authorization_refusal(race)

    def assert_stored_token_and_expiry_belong_to_the_winner(self, race: RotationRace) -> None:
        self.concurrent_rotation_statements.assert_exactly_one_full_rotation_is_stored(race.live, race)

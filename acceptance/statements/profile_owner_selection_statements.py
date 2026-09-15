from clients.application.dto.profile.profile_dto import ProfileDto
from clients.application.profile_client import ProfileClient

from statements.profile_statements import ProfileStatements, SignedInUser

CLIENT_USER_ID_PARAMETER = "userId"
DISTINGUISHING_FIELDS = ("id", "name", "surname", "email", "avatar_id", "city")


class ProfileOwnerSelectionStatements:
    def __init__(self, profile_client: ProfileClient, profile_statements: ProfileStatements):
        self.profile_client = profile_client
        self.profile_statements = profile_statements

    async def sign_in_two_users_with_separate_accounts(self) -> tuple[SignedInUser, SignedInUser]:
        first = await self.profile_statements.sign_in_user_with_every_field_filled()
        second = await self.profile_statements.sign_in_user_with_every_field_filled()
        return first, second

    async def request_own_profile_passing_other_user_identifier(
        self, requester: SignedInUser, other: SignedInUser
    ) -> ProfileDto:
        return await self.profile_client.fetch_profile(
            requester.access_token, params={CLIENT_USER_ID_PARAMETER: other.record.id}
        )

    def assert_request_succeeded(self, profile: ProfileDto) -> None:
        self.profile_statements.assert_request_succeeded(profile)

    def assert_carries_only_requesters_account(self, profile: ProfileDto, requester: SignedInUser) -> None:
        self.profile_statements.assert_carries_every_client_field_name(profile)
        self.profile_statements.assert_values_match_stored_record(profile, requester)

    @staticmethod
    def assert_other_users_data_is_absent(profile: ProfileDto, other: SignedInUser) -> None:
        leaked = {
            field for field in DISTINGUISHING_FIELDS if getattr(profile.record, field) == getattr(other.record, field)
        }
        assert not leaked, (
            f"a client-sent {CLIENT_USER_ID_PARAMETER} must never select another account; "
            f"the response leaked {sorted(leaked)} of the other account"
        )

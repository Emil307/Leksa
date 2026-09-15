import asyncio
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_statements import AuthStatements, is_canonical_uuid
from statements.outbox_database import OutboxDatabase

HTTP_BAD_REQUEST = 400
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
SAMPLE_SIZE = 100
CONCURRENT_REQUESTS = 20
LEADING_ZERO = "0"


@dataclass(frozen=True)
class LeadingZeroCode:
    email: str
    challenge_id: str
    code: str

    @property
    def without_leading_zeros(self) -> str:
        return self.code.lstrip(LEADING_ZERO)


class ChallengeVerifyLeadingZeroStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_a_generated_code_starting_with_zero(self) -> LeadingZeroCode:
        emails = [self.auth_statements.new_user_email() for _ in range(SAMPLE_SIZE)]
        started = await self._request_codes(emails)

        for email, challenge_id in started:
            code = await self.outbox_database.queued_code_for(email)
            assert code is not None, f"a login code must be queued for {email}, the outbox stayed empty"
            if code.startswith(LEADING_ZERO):
                return LeadingZeroCode(email=email, challenge_id=challenge_id, code=code)

        raise AssertionError(
            f"none of the {SAMPLE_SIZE} generated codes started with {LEADING_ZERO!r} — "
            "the generator is expected to emit leading zeros about one time in ten"
        )

    async def verify_code_without_its_leading_zero(self, requested: LeadingZeroCode) -> SessionDto:
        return await self.auth_client.verify_challenge(requested.challenge_id, requested.without_leading_zeros)

    async def verify_code_unchanged(self, requested: LeadingZeroCode) -> SessionDto:
        return await self.auth_client.verify_challenge(requested.challenge_id, requested.code)

    def assert_the_shortened_code_was_rejected(self, session: SessionDto, requested: LeadingZeroCode) -> None:
        assert session.http_status == HTTP_BAD_REQUEST, (
            f"{requested.without_leading_zeros!r} — the code {requested.code!r} with its leading zero dropped — "
            f"is not a six-digit code and must be refused with {HTTP_BAD_REQUEST}, got {session.http_status}"
        )
        assert session.response_field_names == ERROR_ENVELOPE_FIELDS, (
            f"the refusal must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, "
            f"got {sorted(session.response_field_names)}"
        )
        assert session.session_id is None, (
            f"{requested.without_leading_zeros!r} must issue no session, got {session.session_id!r}"
        )

    def assert_session_was_issued(self, session: SessionDto) -> None:
        self.auth_statements.assert_verify_accepted(session)
        assert is_canonical_uuid(session.session_id), (
            f"the issued session must carry a canonical UUID id, got {session.session_id!r}"
        )
        assert is_canonical_uuid(session.user_id), (
            f"the issued session must name a canonical UUID user id, got {session.user_id!r}"
        )
        assert session.refresh_token, "the issued session must carry a refresh token"
        assert session.access_token, "the issued session must carry an access token"

    async def assert_the_queued_code_kept_its_leading_zero(self, requested: LeadingZeroCode) -> None:
        queued = await self.outbox_database.queued_code_for(requested.email)
        assert queued == requested.code, (
            f"the code queued for {requested.email} must stay exactly {requested.code!r}, found {queued!r}"
        )
        assert queued.startswith(LEADING_ZERO) and queued.isdigit(), (
            f"the queued code must remain a digit string opening with {LEADING_ZERO!r}, found {queued!r}"
        )

    async def _request_codes(self, emails: list[str]) -> list[tuple[str, str]]:
        started: list[tuple[str, str]] = []
        for offset in range(0, len(emails), CONCURRENT_REQUESTS):
            batch = emails[offset : offset + CONCURRENT_REQUESTS]
            answers: list[ChallengeStartDto] = await asyncio.gather(
                *(self.auth_statements.request_code(email) for email in batch)
            )
            for email, challenge in zip(batch, answers, strict=True):
                self.auth_statements.assert_challenge_accepted(challenge)
                started.append((email, challenge.challenge_id))
        return started

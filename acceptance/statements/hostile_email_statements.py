import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, AuthClient

from statements.auth_statements import EMAIL_CODE, HTTP_OK, AuthStatements
from statements.outbox_database import OutboxDatabase
from statements.test_data import TestData

HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
VALIDATION_FAILED = "VALIDATION_FAILED"
CONFLICT = "CONFLICT"
LINE_BREAK = "\r\n"
REPLACEMENT_CHARACTER = "\ufffd"
ASTRAL_LEAD = "\U0001f600"
LOOKALIKE_ASTRAL_LEAD = "\U0001f601"


@dataclass(frozen=True)
class StartOutcome:
    email: str
    http_status: int
    error_code: str | None


@dataclass(frozen=True)
class SplitAttempt:
    offered: str
    head: str
    injected_tail: str


@dataclass(frozen=True)
class MultibyteAddresses:
    address: str
    lookalike: str
    folded: str
    replaced: str


class HostileEmailStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    def address_carrying_a_line_break(self) -> SplitAttempt:
        head = self.auth_statements.new_user_email()
        injected_tail = self.auth_statements.new_user_email()
        return SplitAttempt(
            offered=f"{head}{LINE_BREAK}{injected_tail}",
            head=head,
            injected_tail=injected_tail,
        )

    def multibyte_addresses_around_the_masking_boundary(self) -> MultibyteAddresses:
        tail = f"learner-{uuid.uuid4().hex[:12]}@{TestData.EMAIL_DOMAIN}"
        return MultibyteAddresses(
            address=f"{ASTRAL_LEAD}{tail}",
            lookalike=f"{LOOKALIKE_ASTRAL_LEAD}{tail}",
            folded=tail,
            replaced=f"{REPLACEMENT_CHARACTER}{tail}",
        )

    async def request_code_for(self, email: str) -> StartOutcome:
        response = await self.auth_client.post(CHALLENGE_START_PATH, json={"email": email, "challengeType": EMAIL_CODE})
        return StartOutcome(
            email=email,
            http_status=response.status_code,
            error_code=self._error_code(response),
        )

    def assert_rejected_as_invalid_data(self, outcome: StartOutcome) -> None:
        assert outcome.http_status == HTTP_BAD_REQUEST, (
            f"a hostile address must be rejected with {HTTP_BAD_REQUEST}, got {outcome.http_status}"
        )
        assert outcome.error_code == VALIDATION_FAILED, (
            f"a hostile address must answer code {VALIDATION_FAILED!r}, got {outcome.error_code!r}"
        )

    def assert_accepted(self, outcome: StartOutcome) -> None:
        assert outcome.http_status == HTTP_OK, (
            f"the code request for {outcome.email!r} must be accepted with {HTTP_OK}, "
            f"got {outcome.http_status} with code {outcome.error_code!r}"
        )

    async def assert_no_request_was_queued_for(self, *addresses: str) -> None:
        for address in addresses:
            queued = await self.outbox_database.queued_code_for(address)
            assert queued is None, (
                f"a rejected hostile address must queue nothing for {address!r}, found code {queued!r}"
            )

    async def assert_request_was_queued_verbatim_for(self, email: str) -> None:
        queued = await self.outbox_database.queued_code_for(email)
        assert queued is not None, (
            f"an accepted address must reach the queue exactly as sent — no row carries {email!r}"
        )

    async def assert_the_queue_carries_no_mangled_spelling(self, addresses: MultibyteAddresses) -> None:
        mangled = await self.outbox_database.queued_code_for(addresses.replaced)
        assert mangled is None, (
            f"the queued address must keep its multibyte character intact — "
            f"a row spelled with the replacement character {addresses.replaced!r} carries code {mangled!r}"
        )

    async def assert_address_is_on_its_own_cooldown(self, email: str) -> None:
        repeated = await self.request_code_for(email)
        assert repeated.http_status == HTTP_CONFLICT, (
            f"a second code request for {email!r} must hit its own cooldown with {HTTP_CONFLICT}, "
            f"got {repeated.http_status}"
        )
        assert repeated.error_code == CONFLICT, (
            f"the cooldown denial for {email!r} must answer code {CONFLICT!r}, got {repeated.error_code!r}"
        )

    async def assert_address_holds_no_storage_key(self, email: str) -> None:
        outcome = await self.request_code_for(email)
        assert outcome.http_status == HTTP_OK, (
            f"{email!r} must hold no storage key of its own — the next code request for it must be "
            f"accepted with {HTTP_OK}, got {outcome.http_status} with code {outcome.error_code!r}"
        )

    @staticmethod
    def _error_code(response: Any) -> str | None:
        try:
            body = response.json()
        except ValueError:
            return None
        return body.get("code") if isinstance(body, dict) else None

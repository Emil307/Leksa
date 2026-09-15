import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, CHALLENGE_VERIFY_PATH, AuthClient
from httpx import Response

from statements.auth_database import AuthDatabase
from statements.auth_statements import HTTP_OK, AuthStatements, RequestedCode
from statements.outbox_database import OutboxDatabase

HTTP_BAD_REQUEST = 400
VALIDATION_FAILED = "VALIDATION_FAILED"
EMAIL_CODE = "EMAIL_CODE"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
ACCEPTED_STATUSES = (HTTP_OK, HTTP_BAD_REQUEST)
INJECTED_CHALLENGE_ID = "' OR 1=1; DROP TABLE auth.t_sessions; --"
INJECTED_CODE = "1' OR '1'='1"
SQL_TEXT_MARKERS = (
    "select ",
    "insert ",
    "update ",
    "delete ",
    "drop ",
    " from ",
    " where ",
    "--",
    "t_users",
    "t_auth",
    "t_sessions",
    "syntax error",
    "asyncpg",
    "psycopg",
    "sqlalchemy",
)
CONSTRAINT_MARKERS = ("constraint", "duplicate key", "_pkey", "_key", "unique", "violates")


@dataclass(frozen=True)
class RegisteredIdentity:
    email: str
    user_id: str
    session_ids: list[str]


@dataclass(frozen=True)
class InjectionAnswer:
    label: str
    http_status: int
    body: dict[str, Any]
    rendered_body: str


class SqlInjectionStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        auth_database: AuthDatabase,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database
        self.outbox_database = outbox_database

    async def given_registered_user(self) -> RegisteredIdentity:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)
        session = await self.auth_client.verify_challenge(requested.challenge_id, requested.code)
        self.auth_statements.assert_verify_accepted(session)
        return RegisteredIdentity(
            email=email,
            user_id=session.user_id,
            session_ids=await self.auth_database.session_ids_of_user(session.user_id),
        )

    async def given_live_code(self) -> RequestedCode:
        email = self.auth_statements.new_user_email()
        return await self.auth_statements.request_code_and_capture(email)

    def sql_fragment_email(self) -> str:
        return f"bobby');drop--table-{uuid.uuid4().hex[:12]}@uwords-acceptance.local"

    async def request_code_with(self, email: str) -> InjectionAnswer:
        response = await self.auth_client.post(CHALLENGE_START_PATH, json={"email": email, "challengeType": EMAIL_CODE})
        return self._answer("email на запросе кода", response)

    async def verify_with_a_sql_fragment_challenge_id(self, working: RequestedCode) -> InjectionAnswer:
        response = await self.auth_client.post(
            CHALLENGE_VERIFY_PATH, json={"challengeId": INJECTED_CHALLENGE_ID, "code": working.code}
        )
        return self._answer("идентификатор challenge на проверке", response)

    async def verify_with_a_sql_fragment_code(self, working: RequestedCode) -> InjectionAnswer:
        response = await self.auth_client.post(
            CHALLENGE_VERIFY_PATH, json={"challengeId": working.challenge_id, "code": INJECTED_CODE}
        )
        return self._answer("код на проверке", response)

    def assert_refused_as_invalid_data_or_taken_as_an_ordinary_value(self, answer: InjectionAnswer) -> None:
        assert answer.http_status in ACCEPTED_STATUSES, (
            f"«{answer.label}» must be refused as invalid data ({HTTP_BAD_REQUEST}) or taken as an ordinary "
            f"value ({HTTP_OK}), got {answer.http_status} with body {answer.rendered_body}"
        )
        if answer.http_status == HTTP_BAD_REQUEST:
            self._assert_plain_validation_envelope(answer)

    def assert_body_carries_no_sql_text_and_no_constraint_name(self, answer: InjectionAnswer) -> None:
        lowered = answer.rendered_body.lower()
        sql_leaks = [marker for marker in SQL_TEXT_MARKERS if marker in lowered]
        assert not sql_leaks, (
            f"«{answer.label}» must answer without SQL text, found {sql_leaks!r} in {answer.rendered_body}"
        )
        constraint_leaks = [marker for marker in CONSTRAINT_MARKERS if marker in lowered]
        assert not constraint_leaks, (
            f"«{answer.label}» must answer without a database constraint name, "
            f"found {constraint_leaks!r} in {answer.rendered_body}"
        )

    def assert_body_does_not_echo(self, answer: InjectionAnswer, injected: str) -> None:
        assert injected.lower() not in answer.rendered_body.lower(), (
            f"«{answer.label}» must not echo the submitted fragment {injected!r}, got {answer.rendered_body}"
        )

    async def assert_registered_user_untouched(self, user: RegisteredIdentity) -> None:
        users = await self.auth_database.count_users_with_email(user.email)
        assert users == 1, f"the registered user {user.email!r} must survive as exactly one row, found {users}"
        identities = await self.auth_database.email_identity_user_ids(user.email)
        assert identities == [user.user_id], (
            f"the registered user must keep exactly the email identity {[user.user_id]!r}, found {identities!r}"
        )
        sessions = await self.auth_database.session_ids_of_user(user.user_id)
        assert sessions == user.session_ids, (
            f"the registered user must keep exactly the sessions {user.session_ids!r}, found {sessions!r}"
        )

    async def assert_no_account_was_created_for(self, email: str) -> None:
        users = await self.auth_database.count_users_with_email(email)
        assert users == 0, f"a code request must create no account for {email!r}, found {users} row(s)"
        identities = await self.auth_database.email_identity_user_ids(email)
        assert identities == [], f"a code request must create no email identity for {email!r}, found {identities!r}"

    async def assert_queued_code_carries_the_address_verbatim(self, email: str) -> None:
        queued = await self.outbox_database.queued_code_for(email)
        assert queued is not None, (
            f"an accepted code request must queue a code stored under the verbatim address {email!r}, "
            "the outbox stayed empty"
        )

    async def assert_live_code_still_issues_a_session(self, working: RequestedCode) -> None:
        session = await self.auth_client.verify_challenge(working.challenge_id, working.code)
        self.auth_statements.assert_verify_accepted(session)
        assert session.refresh_token, "the untouched challenge must still answer with a refresh token"
        assert session.access_token, "the untouched challenge must still answer with an access token"

    def _assert_plain_validation_envelope(self, answer: InjectionAnswer) -> None:
        assert answer.body.get("code") == VALIDATION_FAILED, (
            f"«{answer.label}» must answer error code {VALIDATION_FAILED}, got {answer.body.get('code')!r}"
        )
        assert frozenset(answer.body) == ERROR_ENVELOPE_FIELDS, (
            f"«{answer.label}» must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(answer.body)}"
        )

    def _answer(self, label: str, response: Response) -> InjectionAnswer:
        return InjectionAnswer(
            label=label,
            http_status=response.status_code,
            body=self._body_of(response),
            rendered_body=response.text,
        )

    @staticmethod
    def _body_of(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}

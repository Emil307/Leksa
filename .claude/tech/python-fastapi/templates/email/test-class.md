# Email Adapter Test Template — python-fastapi

## Test Class Rules

- `class TestXSender:` with `@pytest.mark.asyncio` `async def test_should_{behavior}` methods.
- Capture sent mail with a test SMTP sink: an in-memory `FakeMailTransport` injected into the sender, or MailHog's HTTP API when the scenario needs the real SMTP path.
- Never assert against a live mailbox — the transport is injected, not patched globally.
- Class-level docstring with a Gherkin-style description.
- Assert recipient, subject, and the **rendered** body (template placeholders substituted).

## Email-Specific Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| `raise NotImplementedError()` | `NotImplementedError` |
| empty method body (nothing sent) | `assert len(transport.sent) == 1` fails with 0 |
| wrong template used | body mismatch on the rendered assertion |
| placeholder not substituted | `assert TOKEN in message.html_body` fails |

## Reference (read before generating)

- Sender base: `backend/adapters/email/src/senders/_base.py`
- Existing sender: `backend/adapters/email/src/senders/notification_sender.py`
- Port `Protocol`: `backend/usecase/src/ports/notification_sender.py`
- Templates: `backend/adapters/email/src/templates/`
- Fake transport fixture: `backend/adapters/email/tests/conftest.py`

## Test Pattern

1. **Setup** (fixture): construct the sender with `FakeMailTransport` and a `FakeClock`.
2. **Execute**: `await sender.send(...)`.
3. **Assert**: exactly one message; recipient, subject, content type, rendered body.

## Naming

- Test file: `backend/adapters/email/tests/senders/test_{sender}.py`
- Test method: `test_should_{expected_behavior}`

# Email Adapter Implementation Template — python-fastapi

## Rules

- Implement the port `Protocol` declared in `backend/usecase/src/ports/` (e.g. `NotificationSender`) — the usecase never imports the adapter.
- Extend the shared `AbstractMailSender` for template loading and transport handling.
- Async send via `aiosmtplib`; the transport is injected through `__init__` so tests can pass a fake.
- HTML templates live in `backend/adapters/email/src/templates/`, `{placeholder}` syntax for dynamic values.
- SMTP host/port/credentials come from `pydantic-settings` (`settings.smtp.*`) — never hardcoded.

## Shape

```python
class PasswordResetSender(AbstractMailSender):
    async def send(self, recipient: str, token: str) -> None:
        body = self.load_template("password_reset.html").replace("{token}", token)
        await self.send_html_email(to=recipient, subject="Reset your password", body=body)
```

## Reference

- Abstract base: `backend/adapters/email/src/senders/_base.py`
- Existing sender: `backend/adapters/email/src/senders/notification_sender.py`
- Ports: `backend/usecase/src/ports/`

## Verify

- `pytest backend/adapters/email/tests/senders/test_{sender}.py` GREEN. File ≤ 200 lines.

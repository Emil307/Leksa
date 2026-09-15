# Bot API Client Test Template — python-aiogram

## Location

`bot/tests/api/test_{resource}_api_client.py`

## Rules

- Use a strict `httpx.MockTransport` or equivalent transport.
- Assert HTTP method, path, headers, and serialized body exactly inside the transport.
- Return a complete representative response and assert the complete typed result.
- Test API error responses separately from network/timeout failures.
- No live API, database, or API application imports.

## Failure Patterns

| Stub/current state | Expected failure |
|---|---|
| client method missing | import or attribute error |
| wrong request | strict transport assertion fails |
| response not parsed | typed-result equality fails |
| transport error not mapped | raw transport exception escapes |

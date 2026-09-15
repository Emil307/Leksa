# Security Adapter Test Template — python-fastapi

## Test Class Rules

- Pure unit tests — no ASGI client, no DB, no `TestClient`.
- Construct the class under test manually in a fixture; inject collaborators as `Mock`/`AsyncMock`.
- Time is injected: `FakeClock(FIXED_NOW)`, never `datetime.now()` — expiry assertions must be deterministic.
- Class-level docstring with a Gherkin-style description.
- Cover the rejection paths (expired, tampered, missing, wrong audience), not just the happy path.

## Security-Specific Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| `raise NotImplementedError()` | `NotImplementedError` |
| token issued without a claim | `assert claims["sub"] == ...` KeyError / mismatch |
| verification accepts anything | `pytest.raises(InvalidTokenException)` does not raise |
| expiry computed from wall clock | expiry assertion off by the test's runtime |

## Reference (read before generating)

- JWT service: `backend/adapters/security/src/jwt_service.py`
- Config: `backend/adapters/security/src/jwt_config.py`
- Auth dependency (FastAPI `Depends`): `backend/adapters/security/src/dependencies.py`
- Existing test: `backend/adapters/security/tests/test_jwt_service.py`

## Test Pattern

1. **Setup** (fixture): config + `FakeClock` + class under test.
2. **Execute**: call the method under test.
3. **Assert**: decode the token and assert each claim exactly; assert each rejection raises its own domain exception.

## Naming

- Test file: `backend/adapters/security/tests/test_{component}.py`
- Test method: `test_should_{expected_behavior}`

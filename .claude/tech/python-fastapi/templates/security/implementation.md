# Security Adapter Implementation Template — python-fastapi

## Rules

- Minimal code to pass the failing test (tests READ-ONLY in GREEN).
- JWT operations via `JwtService` (PyJWT); configuration via a `JwtConfig` Pydantic settings model — secrets come from `.env`, never literals in code.
- Time via an injected `Clock` protocol (`FakeClock` in tests).
- Authentication is exposed to routers as a FastAPI dependency (`Depends(get_current_user)`) living in this adapter — routers never decode tokens themselves.
- Failures raise domain exceptions (`InvalidTokenException`, `TokenExpiredException`) that the centralized `@app.exception_handler` maps to 401/403.
- The adapter implements the port `Protocol` declared in `backend/usecase/src/ports/` when a usecase needs token issuing.

## Shape

```python
class JwtService:
    def __init__(self, config: JwtConfig, clock: Clock):
        self.config = config
        self.clock = clock

    def issue(self, user_id: UUID) -> str:
        expires_at = self.clock.now() + timedelta(seconds=self.config.ttl_seconds)
        claims = {"sub": str(user_id), "exp": int(expires_at.timestamp())}
        return jwt.encode(claims, self.config.secret, algorithm=self.config.algorithm)
```

## Reference

- JWT service: `backend/adapters/security/src/jwt_service.py`
- Config: `backend/adapters/security/src/jwt_config.py`
- Auth dependency: `backend/adapters/security/src/dependencies.py`

## Verify

- `pytest backend/adapters/security/tests/test_{component}.py` GREEN. File ≤ 200 lines.

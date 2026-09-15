# Test Review Patterns: REST Adapter Layer (Python/FastAPI)

Python/`unittest.mock` code examples for router test anti-patterns. For universal rules: `.claude/templates/testing/test-review-patterns.md`

## Python-Specific Rules (REST)

1. **Add an assertion message** — `assert resp.status_code == 201, "created status"`.
2. **Use exact expected values in mock setups** — `mock.assert_awaited_once_with(expected_request)` instead of `assert_awaited()`. Pydantic request models already implement `__eq__`, so exact matching costs nothing and catches router mapping bugs.
3. **No `unittest.mock.ANY` when the exact value is known.**
4. **Assert status AND body** — a router test that checks only `status_code` does not pin the response mapping.
5. **`AsyncMock`, not `Mock`, for async services** — a plain `Mock` returns a coroutine-less value and the router silently awaits a `MagicMock`.

## Anti-Pattern Examples

### BAD: Loose mock matching (universal #21) — three forms, one fix
```python
service.create_task.assert_awaited_once_with(USER_ID, unittest.mock.ANY)   # wildcard
service.create_task.assert_awaited_once()                                  # no arguments at all
args, kwargs = service.create_task.call_args                               # hand-picked fields
assert args[1].title == "Design"
# GOOD: one exact match — Pydantic request models implement __eq__
service.create_task.assert_awaited_once_with(USER_ID, TaskCreate(title="Design", column_id=COLUMN_ID))
```

### BAD: Status-only assertion, happy path and error path alike (universal #12)
```python
assert resp.status_code == 200      # response mapping unpinned
assert resp.status_code == 404      # error contract unpinned
# GOOD: status AND parsed body, on both paths
assert resp.status_code == 200, "ok status"
assert resp.json() == {"id": str(TASK_ID), "title": "Design", "status": "todo"}
assert resp.status_code == 404, "not found status"
assert resp.json()["code"] == ErrorCode.TASK_NOT_FOUND.value, "error code"
```

### BAD: `Mock()` for an async service
```python
service = Mock()
service.create_task.return_value = task   # router awaits a non-awaitable
# GOOD
service = AsyncMock()
service.create_task.return_value = task
```

### BAD: Real DB reached from a router test
```python
app.dependency_overrides = {}          # falls through to the real repository
# GOOD: override the dependency with a fake/AsyncMock service
app.dependency_overrides[get_task_service] = lambda: service
```

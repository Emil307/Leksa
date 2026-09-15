# Test Review Patterns: Acceptance Layer (Python/FastAPI)

Python/httpx code examples for black-box acceptance test anti-patterns. For universal rules: `.claude/templates/testing/test-review-patterns.md`

## Python-Specific Rules (Acceptance)

1. **Parse, then assert** — the client parses the response into a DTO once; Statements assert on DTO fields, never against raw response text.
2. **No `httpx.` anywhere above the client tier** — neither in the test class nor in Statements. `httpx`, URL construction, and `resp.status_code` live only in `acceptance/clients/application/` (test-review item 26).
3. **Assert status AND body on every request** — a 200 with the wrong payload is the failure acceptance tests exist to catch. The client surfaces the status; Statements assert it alongside the fields.
4. **Values known from setup must be asserted exactly** — if the test created the task, its title is deterministic.

## Anti-Pattern Examples

### BAD: Loose string validation
```python
assert "Design" in resp.text
# GOOD
assert resp.json()["title"] == "Design", "task title"
```

### BAD: Chained `in` checks
```python
assert "todo" in body and "Design" in body
# GOOD: one exact object comparison
assert body == {"id": task_id, "title": "Design", "status": "todo"}
```

### BAD: `is not None` for a value the test controls
```python
created = await task_statements.create_task(login)
assert created.due_date is not None
# GOOD: capture from setup, assert exact
assert created.due_date == EXPECTED_DUE_DATE, "due date"
```

### BAD: Missing field assertions
```python
assert body["id"] == task_id
# MISSING: title, status, assignee, priority, due_date
# GOOD: assert the whole documented payload
assert body == expected_payload
```

### BAD: Asserting only the first item of a collection
```python
assert body["tasks"][0]["title"] == "Design"
# tasks[1] and tasks[2] are never checked
# GOOD
assert [t["title"] for t in body["tasks"]] == ["Design", "Build", "Ship"]
```

### BAD: Timestamp assertion without a real comparison
```python
assert body["created_at"] is not None
# GOOD: bounded against the test clock
created_at = datetime.fromisoformat(body["created_at"])
assert abs(created_at - now) < timedelta(seconds=60), "created_at within a minute"
```

### BAD: Range check when the value is deterministic
```python
assert body["days_remaining"] > 0
# GOOD
assert body["days_remaining"] == 7, "days remaining"
```

### BAD: `httpx` in the test class
```python
async def test_should_create_task(self, client):
    resp = await client.post("/tasks", json={"title": "Design"})   # HTTP leak
    assert resp.status_code == 201
# GOOD: Statements own the DSL, the client owns the call
async def test_should_create_task(self):
    response = await task_statements.create_task(title="Design")
    await task_statements.assert_task_listed(response)
```

### BAD: `httpx` in Statements
```python
class TaskStatements:
    async def create_task(self, title: str) -> str:
        resp = await self.http.post(f"{self.base_url}/tasks", json={"title": title})   # client-tier work
        return resp.json()["id"]
# GOOD: Statements call the client and assert on the DTO
class TaskStatements:
    async def create_task(self, title: str) -> TaskDto:
        created = await self.task_client.create(CreateTaskRequest(title=title))
        assert created.title == title, "task title"
        return created
```

### BAD: Empty collections in expected values
```python
assert response.permissions == []
# GOOD: assert the values the scenario actually grants
assert response.permissions == ["Read", "Write"], "permissions"
```

### BAD: `in` on a collection instead of exact match
```python
assert "Design" in [t.title for t in body.tasks]
# GOOD: the whole collection is deterministic
assert [t.title for t in body.tasks] == ["Design", "Build", "Ship"], "task titles"
```

### BAD: Asserting only IDs without full object contents
```python
assert task.id == EXPECTED_ID
# MISSING: title, status, assignee, priority, due_date
# GOOD: compare the whole DTO
assert task == EXPECTED_TASK
```

### BAD: Bare `asyncio.sleep` waiting for an async side effect
```python
await asyncio.sleep(2)
assert (await task_statements.list_tasks())[0]["status"] == "done"
# GOOD: poll the assertion with tenacity
@retry(stop=stop_after_delay(5), wait=wait_fixed(0.1))
async def assert_task_done():
    tasks = await task_statements.list_tasks()
    assert tasks[0]["status"] == "done", "task status"
```

## Correct Patterns

### GOOD: Parse in the client, assert in Statements
```python
# acceptance/clients/application/task_client.py — the ONLY tier importing httpx
class TaskClient:
    async def create(self, request: CreateTaskRequest) -> ClientResponse[TaskDto]:
        resp = await self._http.post(f"{self._base_url}/tasks", json=asdict(request))
        return ClientResponse(status=resp.status_code, body=TaskDto(**resp.json()))

# acceptance/statements/task_statements.py — no httpx, no URLs
async def assert_task_created(self, expected_title: str) -> TaskDto:
    response = await self.task_client.create(CreateTaskRequest(title=expected_title))
    assert response.status == 201, "created status"
    assert response.body.title == expected_title, "task title"
    assert response.body.status == TaskStatus.TODO.value, "initial status"
    return response.body
```

### GOOD: Error responses assert the documented contract
```python
response = await self.task_client.create(CreateTaskRequest(title=""))
assert response.status == 422, "validation status"
assert response.error.code == ErrorCode.VALIDATION_FAILED.value, "error code"
```

### GOOD: Collection assertions with expected constants
```python
EXPECTED_PERMISSIONS = ["Read", "Write"]
assert response.body.permissions == EXPECTED_PERMISSIONS, "token permissions"
```

### GOOD: Complete response validation
```python
async def assert_task_matches(self, actual: TaskDto) -> None:
    assert actual.title == EXPECTED_TITLE, "title"
    assert actual.description == EXPECTED_DESCRIPTION, "description"
    assert actual.column_id == EXPECTED_COLUMN_ID, "column id"
    assert actual.status == EXPECTED_STATUS, "status"
    assert actual.created_at > self.clock.now() - timedelta(seconds=30), "created at"
```

### GOOD: Dataclass equality instead of per-field assertions
```python
# Replace 2+ per-field assertions with one comparison —
# frozen DTOs compare all fields recursively
assert actual == EXPECTED_TASK, "task payload"
```

### GOOD: Extract a validation helper for structured headers
```python
# Parsing a Set-Cookie header inline hides what is being asserted.
# A small helper in the client tier exposes named properties instead.
cookie = SetCookie(response.headers)
assert cookie.name == "session", "cookie name"
assert cookie.max_age == "3600", "cookie max age"
assert cookie.http_only is True, "HttpOnly flag"
```

## Assertion Improvements (Python/pytest syntax)

| Loose | Strict |
|-------|--------|
| `assert x in resp.text` | `assert resp.json()["field"] == x` |
| `assert x is not None` | `assert x == expected` |
| `assert len(items) > 0` | `assert items == [expected_a, expected_b]` |
| `assert value > 0` | `assert value == 7` |
| `assert ts is not None` | `assert abs(ts - now) < timedelta(seconds=60)` |

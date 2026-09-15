# Test Review Patterns: Usecase Layer (Python/FastAPI)

Python/pytest code examples for usecase test anti-patterns. For universal rules: `.claude/templates/testing/test-review-patterns.md`

## Python-Specific Rules (Usecase)

1. **Add an assertion message** — `assert actual == expected, "task status"` so the failure names the field.
2. **No `NotImplementedError` in Statements** — Python marker for the universal rule (`tdd-rules.md`: Statements must be fully functional in RED).
3. **Prefer model equality** — replace 2+ sequential per-field asserts with `assert actual == expected` (Pydantic models and frozen dataclasses compare deeply).
4. **`await` belongs in the test class, the call belongs in Statements** — `await task_statements.create_task(login)`, never `await self.create_task_service.execute(...)` in the test class.

## Anti-Pattern Examples

### BAD: Infrastructure leaking into the test class
```python
repository_fake.given_task_saved(task)
response = await create_task_service.execute(request)
assert response.status == TaskStatus.TODO
# GOOD: hide behind Statements — the test reads like business DSL
response = await task_statements.create_task(login_response)
await task_statements.assert_task_created(response)
```

### BAD: Direct service call in the test class
```python
task_response = await create_task.execute(task_request)  # usecase leak
# GOOD: Statements wraps the usecase call
task_response = await task_statements.given_task_created(login_response)
```

### BAD: Any assertion in the test class
```python
async def test_should_reject_unknown_task(self):
    login = await login_statements.login()
    with pytest.raises(TaskNotFoundException):
        await list_statements.get_tasks(login.user_id)
# GOOD: all assertions in Statements
async def test_should_reject_unknown_task(self):
    login = await login_statements.login()
    await list_statements.assert_rejects_unknown_task(login.user_id)
```

### BAD: Private function or nested class in the test class
```python
class TestEditTask:
    async def _given_user_with_task(self):  # belongs in Statements
        login = await user_statements.given_registered_user()
        return login, await task_statements.create_task(login)
# GOOD: test class has zero private members
class TestEditTask:
    async def test_should_reject_empty_name(self):
        setup = await task_statements.given_user_with_task()
```

### BAD: Setup step visible in test DSL
```python
login = await setup_statements.login_and_setup_data()
await setup_statements.setup_test_data(login)   # infrastructure leak
await setup_statements.execute_action()
# GOOD: merge setup into one compound given-phase method
login = await setup_statements.login_and_setup_data_with_tasks()
await setup_statements.execute_action()
```

### BAD: Cross-Statements data passing in the test class
```python
login_response = await auth_statements.login(auth_statements.login_request())
await auth_statements.assert_session_created(login_response)
await reset_statements.reset_password(
    await reset_statements.request_reset_and_get_token(
        user_statements.register_request()))
# GOOD: compound methods hide all coordination
await auth_statements.assert_test_user_can_login()
await reset_statements.reset_test_user_password()
await reset_statements.assert_can_login_with_new_password()
```

### BAD: Decomposed call when a compound method exists
```python
await auth_statements.login(auth_statements.login_request())
# GOOD: use the existing compound
await auth_statements.login_test_user()
```

### BAD: Scope construction in the test class
```python
request = TaskScope.builder(title="Design").to_request()
response = await create_task.execute(request)
# GOOD: Statements owns scope construction
response = await task_statements.given_task_created(title="Design")
```

### BAD: Action + assertion combined in one Statements method
```python
async def assert_task_not_found(self, login):
    with pytest.raises(TaskNotFoundException, match="Task not found"):
        await self.create_task.execute(self._build_request(login))
# GOOD: split into action + assertion
async def create_task_for_missing_column(self, login):
    try:
        await self.create_task.execute(self._build_request(login))
    except BaseDomainException as e:
        self.thrown_exception = e

def assert_task_not_found(self):
    assert isinstance(self.thrown_exception, TaskNotFoundException)
    assert self.thrown_exception.code == ErrorCode.TASK_NOT_FOUND
```

### BAD: Fake repository injected into Statements (verification)
```python
def assert_task_recorded(self, task_id, expected_status):
    tasks = self.fake_task_repository.find_by_id(task_id)   # storage leak
    assert tasks[0].status == expected_status
# GOOD: verify through the reading usecase
async def assert_task_recorded(self, task_id, expected_status):
    task = await self.get_task_service.execute(task_id)
    assert task.status == expected_status, "task status"
```

### BAD: Fake repository injected into Statements (setup)
```python
async def given_task_recorded(self, task_id, status):
    self.fake_task_repository.save(Task(id=task_id, status=status))
# GOOD: set up through the writing usecase
async def given_task_recorded(self, title, status):
    return await self.create_task_service.execute(TaskCreate(title=title, status=status))
```

### BAD: `AsyncMock` standing in for the whole repository
```python
repo = AsyncMock()
repo.get_by_id.return_value = Task(...)   # mock-of-mock, no real behavior
# GOOD: an in-memory fake implementing the port Protocol
repo = FakeTaskRepository()
await repo.create(TaskCreate(title="Design"))
```

### BAD: Duplicating assertion logic from another Statements class
```python
async def assert_task_blocked(self, user_id):
    status = await self.get_task_status.execute(user_id)
    assert status.status == "blocked"
    assert status.column_id == self.column_id
# GOOD: inject the existing Statements and delegate
async def assert_task_blocked(self, user_id, task_id):
    response = await self.get_task_status.execute(user_id)
    self.status_statements.assert_blocked_task(response, task_id)
```

### BAD: Unreferenced domain fields left over from RED
```python
class Column(DomainEntity):
    name: str
    tasks: list[Task]   # no test references tasks -> remove (and delete Task if unused)
# GOOD: only the field the test asserts
class Column(DomainEntity):
    name: str
```

## Correct Patterns

### GOOD: Model equality instead of per-field assertions
```python
assert actual == Task(id=task_id, title="Design", status=TaskStatus.TODO)
```

### GOOD: Exception assertions carry the code
```python
with pytest.raises(ValidationException) as exc:
    await service.create_task(TaskCreate(title=""))
assert exc.value.code == ErrorCode.VALIDATION_FAILED
```

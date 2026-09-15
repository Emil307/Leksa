# Test Review Patterns: Storage Adapter Layer (Python/FastAPI)

Python/pytest code examples for persistence adapter test anti-patterns. For universal rules: `.claude/templates/testing/test-review-patterns.md`

## Python-Specific Rules (Storage)

1. **Add an assertion message** — `assert actual == expected, "task after round-trip"`.
2. **Prefer model equality** — replace 2+ per-field asserts with `assert actual == expected` (Pydantic entities compare deeply).
3. **Timestamps via `timedelta`** — `assert abs(actual - expected) < timedelta(seconds=60)`. Never truncate to minutes; truncation flakes at minute boundaries.
4. **Assert on domain entities, never on `XModel`** — a test that asserts `model.title` bypasses the mapper, which is the thing under test.
5. **`await` every repository call** — an un-awaited coroutine makes the test pass without touching the DB.

## Anti-Pattern Examples

### BAD: Loose existence check after a round-trip
```python
result = await repository.get_by_id(task_id)
assert result is not None
# GOOD: full entity equality — this is what pins the mapper
assert result == Task(id=task_id, title="Design", status=TaskStatus.TODO, created_at=created_at)
```

### BAD: Asserting on the ORM model
```python
model = await session.get(TaskModel, task_id)
assert model.title == "Design"      # mapper never exercised
# GOOD: assert the mapped domain entity
task = await repository.get_by_id(task_id)
assert task.title == "Design", "mapped title"
```

### BAD: Partial field assertions after `to_domain()`
```python
assert task.title == "Design"
# MISSING: status, column_id, created_at, assignee — a dropped mapper field passes
# GOOD: assert the whole entity
assert task == expected_task
```

### BAD: Timestamp truncation
```python
assert task.created_at.replace(second=0, microsecond=0) == now.replace(second=0, microsecond=0)
# GOOD: bounded comparison
assert abs(task.created_at - now) < timedelta(seconds=60), "created_at within a minute"
```

### BAD: Same-port save→read round-trip standing in for the real flow
```python
await repository.create(task_create)
assert await repository.get_by_id(task_id) == expected
# GOOD: write through the writer's port, read through the reader's port
await task_write_repository.create(task_create)
assert await task_query_repository.list_for_column(column_id) == [expected]
```

### BAD: Test leaks state into the next test
```python
async def test_should_store_task(self, session):
    await repository.create(task_create)      # never rolled back
# GOOD: transactional fixture rolls back (or truncates) per test
@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        trx = await conn.begin()
        yield async_session(bind=conn)
        await trx.rollback()
```

### BAD: Unordered query result compared as an ordered list
```python
assert await repository.list_all() == [task_a, task_b]   # no ORDER BY in the query
# GOOD: assert the set, or add a deterministic ORDER BY and keep the list
assert set(await repository.list_all()) == {task_a, task_b}
```

See `test-review-usecase.md` for Statements purity patterns and `test-review-acceptance.md` for assertion strictness — both apply to storage tests.

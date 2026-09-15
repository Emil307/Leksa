# Scheduling Adapter Implementation Template — python-fastapi

## Rules

- Jobs are `AsyncIOScheduler` jobs registered by the app factory's `lifespan`.
- A job delegates immediately to ONE usecase — no business logic in the job body.
- Cron expressions and lock durations come from `pydantic-settings` (`settings.scheduling.*`), never hardcoded.
- The backend runs as multiple instances: every job takes a **distributed lock** (a Postgres advisory lock or a `SELECT ... FOR UPDATE SKIP LOCKED` row) before doing work. An unlocked job runs N times per tick.
- Constructor injection of the usecase — no module-level lookups inside the job.

## Shape

```python
class CleanupJob:
    def __init__(self, usecase: CleanupUsecase, lock: DistributedLock):
        self.usecase = usecase
        self.lock = lock

    async def run(self) -> None:
        async with self.lock.acquire("cleanup", ttl=self.config.lock_seconds) as held:
            if held:
                await self.usecase.execute()

scheduler.add_job(job.run, CronTrigger.from_crontab(settings.scheduling.cleanup_cron))
```

## Reference

- Scheduler setup / lifespan registration: `backend/adapters/scheduling/src/scheduler.py`
- Config: `backend/adapters/scheduling/src/config.py`
- Usecase ports: `backend/usecase/src/`

## Verify

- `pytest backend/adapters/scheduling/tests/jobs/test_{job}.py` GREEN. File ≤ 200 lines.

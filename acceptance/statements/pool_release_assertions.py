import os
from dataclasses import dataclass

POOL_SIZE_VARIABLE = "DB_POOL_SIZE"
APPLICATION_DEFAULT_POOL_SIZE = 10
OVERFLOW_FACTOR = 2

REQUESTS_PER_OUTCOME = 24
SLOWEST_ACCEPTABLE_SECONDS = 5.0


def configured_pool_capacity() -> int:
    declared = os.environ.get(POOL_SIZE_VARIABLE) or str(APPLICATION_DEFAULT_POOL_SIZE)
    return OVERFLOW_FACTOR * int(declared)


@dataclass(frozen=True)
class PoolAttempt:
    outcome_name: str
    expected_status: int
    http_status: int
    seconds: float


def assert_every_outcome_was_driven_past_pool_capacity(attempts: list[PoolAttempt]) -> None:
    capacity = configured_pool_capacity()
    for name in sorted({attempt.outcome_name for attempt in attempts}):
        driven = sum(1 for attempt in attempts if attempt.outcome_name == name)
        assert driven > capacity, (
            f"the {name} outcome must be driven more than {capacity} times — a pool of that capacity "
            f"only reveals a leak once every connection is consumed, got {driven}"
        )


def assert_every_attempt_reached_its_outcome(attempts: list[PoolAttempt]) -> None:
    for index, attempt in enumerate(attempts, start=1):
        assert attempt.http_status == attempt.expected_status, (
            f"attempt {index} of {len(attempts)} on the {attempt.outcome_name} outcome must answer "
            f"{attempt.expected_status}, got {attempt.http_status} — "
            "an earlier outcome kept its connection instead of returning it to the pool"
        )


def assert_no_attempt_waited_for_a_connection(attempts: list[PoolAttempt]) -> None:
    slowest = max(attempts, key=lambda attempt: attempt.seconds)
    assert slowest.seconds < SLOWEST_ACCEPTABLE_SECONDS, (
        f"the {slowest.outcome_name} outcome answered in {slowest.seconds:.2f}s, over the "
        f"{SLOWEST_ACCEPTABLE_SECONDS:.2f}s budget — the request queued for a connection that a "
        "previous outcome never released"
    )


def assert_answered_without_waiting_for_a_connection(seconds: float, subject: str) -> None:
    assert seconds < SLOWEST_ACCEPTABLE_SECONDS, (
        f"{subject} answered in {seconds:.2f}s, over the {SLOWEST_ACCEPTABLE_SECONDS:.2f}s budget — "
        "it queued for a connection"
    )

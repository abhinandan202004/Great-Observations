"""SLA timers derived from an incident's status history (context.md section 5.1)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from infrawatch_core.lifecycle import Status


@dataclass(frozen=True)
class Policy:
    acknowledge: timedelta
    resolve: timedelta


@dataclass(frozen=True)
class Timer:
    due: datetime
    stopped_at: datetime | None  # when the target was met; None while the clock runs
    remaining: timedelta  # negative once overdue; fixed once stopped
    breached: bool


def _timer(
    start: datetime, allowed: timedelta, stopped_at: datetime | None, now: datetime
) -> Timer:
    due = start + allowed
    end = stopped_at or now
    return Timer(due=due, stopped_at=stopped_at, remaining=due - end, breached=end > due)


def timers(
    events: Sequence[tuple[datetime, Status]], policy: Policy, now: datetime
) -> tuple[Timer, Timer]:
    """The acknowledge and resolve timers for events in order, the first being Raised.

    Both clocks start at Raised. Acknowledge stops at the first Acknowledged and never restarts.
    Resolve stops at the latest Resolved while the incident stays Resolved or Closed; a reopen
    restarts it, counting from Raised, so time already spent is not forgiven.
    """
    raised = events[0][0]
    acknowledged = next((t for t, s in events if s is Status.ACKNOWLEDGED), None)
    resolved = None
    if events[-1][1] in (Status.RESOLVED, Status.CLOSED):
        resolved = next(t for t, s in reversed(events) if s is Status.RESOLVED)
    return (
        _timer(raised, policy.acknowledge, acknowledged, now),
        _timer(raised, policy.resolve, resolved, now),
    )

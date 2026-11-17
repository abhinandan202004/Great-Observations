"""The incident status lifecycle from context.md section 5, as pure functions."""

from enum import StrEnum


class Status(StrEnum):
    RAISED = "raised"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Severity(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Move(StrEnum):
    FORWARD = "forward"  # one step on, up to Resolved
    REGRESSION = "regression"  # back to an earlier active state; reason required
    REOPEN = "reopen"  # the caller rejects a resolution; reason required
    CLOSE = "close"  # the caller closes; needs an approved runbook


ACTIVE = (
    Status.RAISED,
    Status.ACKNOWLEDGED,
    Status.INVESTIGATING,
    Status.MITIGATING,
    Status.MONITORING,
)
NEEDS_REASON = frozenset({Move.REGRESSION, Move.REOPEN})


class TransitionError(ValueError):
    """The transition is not in the lifecycle table; the API must refuse it."""


def classify(current: Status, target: Status) -> Move:
    """Name the move from ``current`` to ``target``, or raise if the table does not list it."""
    if current in ACTIVE:
        here = ACTIVE.index(current)
        if target in ACTIVE and ACTIVE.index(target) < here:
            return Move.REGRESSION
        if (*ACTIVE, Status.RESOLVED)[here + 1] is target:
            return Move.FORWARD
    if current is Status.RESOLVED:
        if target is Status.INVESTIGATING:
            return Move.REOPEN
        if target is Status.CLOSED:
            return Move.CLOSE
    raise TransitionError(f"An incident cannot move from {current} to {target}")

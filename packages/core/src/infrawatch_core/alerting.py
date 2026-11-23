"""Static threshold rules with a duration condition (context.md section 8.5), as pure functions."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class Comparator(StrEnum):
    ABOVE = "above"
    BELOW = "below"


@dataclass(frozen=True)
class Rule:
    comparator: Comparator
    threshold: float
    duration: timedelta


def breaches(rule: Rule, value: float) -> bool:
    if rule.comparator is Comparator.ABOVE:
        return value > rule.threshold
    return value < rule.threshold


def firing_since(
    rule: Rule, samples: Sequence[tuple[datetime, float]], now: datetime, stale: timedelta
) -> datetime | None:
    """When the current breach began, if it has lasted the rule's duration; otherwise None.

    ``samples`` are in time order. The breach is the unbroken run of breaching samples ending at
    the newest one, so a single normal sample resets it. A newest sample older than ``stale``
    means the data stopped, and silence never fires.
    """
    if not samples or now - samples[-1][0] > stale:
        return None
    start = None
    for time, value in reversed(samples):
        if not breaches(rule, value):
            break
        start = time
    if start is None or samples[-1][0] - start < rule.duration:
        return None
    return start

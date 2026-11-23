"""Escalation of an unacknowledged incident along a team's on-call rotation."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from infrawatch_core.oncall import Rotation, current_shift


@dataclass(frozen=True)
class Escalation:
    step: int  # 1 for the first escalation, 2 for the next, ...
    from_member: str  # whoever is on call now
    to_member: str


def next_escalation(
    rotation: Rotation, raised_at: datetime, now: datetime, every: timedelta, done: int
) -> Escalation | None:
    """The escalation due now, given ``done`` already made for this team; None if none is due.

    One step falls due each ``every`` after the raise, passing to the next person after the
    on-call. It stops once everyone else in the rotation has been asked, and never starts for a
    team with nobody on call (that team's admin flag covers it).
    """
    shift = current_shift(rotation, now)
    if shift is None or done >= len(rotation.members) - 1:
        return None
    step = done + 1
    if now < raised_at + step * every:
        return None
    target = rotation.members[(shift.index + step) % len(rotation.members)]
    return Escalation(step=step, from_member=shift.member, to_member=target)

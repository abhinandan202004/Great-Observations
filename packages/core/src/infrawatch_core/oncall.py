"""On-call rotations: an ordered list of people taking fixed shifts from a handover time.

The handover is a wall-clock time in a named time zone, so a Monday 09:00 handover stays at
09:00 local time across daylight-saving changes, even though the shift is then an hour longer
or shorter in absolute time.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Rotation:
    members: Sequence[str]  # in rotation order
    handover: datetime  # naive wall-clock time of the first handover in time_zone
    time_zone: str  # IANA name, e.g. "Asia/Kolkata"
    shift_days: int


@dataclass(frozen=True)
class Shift:
    index: int  # position in members of whoever is on call
    member: str
    ends_at: datetime  # aware, the next handover


def current_shift(rotation: Rotation, now: datetime) -> Shift | None:
    """Who is on call at ``now`` (aware), or None before the first handover or with no members."""
    if not rotation.members:
        return None
    zone = ZoneInfo(rotation.time_zone)
    # Count shifts in wall-clock time, so each handover lands on the same local time of day.
    elapsed = now.astimezone(zone).replace(tzinfo=None) - rotation.handover
    if elapsed < timedelta(0):
        return None
    shift = timedelta(days=rotation.shift_days)
    count = elapsed // shift
    index = count % len(rotation.members)
    ends = (rotation.handover + (count + 1) * shift).replace(tzinfo=zone)
    return Shift(index=index, member=rotation.members[index], ends_at=ends)

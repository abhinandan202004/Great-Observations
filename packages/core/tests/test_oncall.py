from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from infrawatch_core.oncall import Rotation, current_shift

LONDON = ZoneInfo("Europe/London")
# Weekly handover at Monday 09:00 London time, starting 2026-03-23.
WEEKLY = Rotation(("asha", "ben", "chen"), datetime(2026, 3, 23, 9, 0), "Europe/London", 7)


def at(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=LONDON)


def who(now: datetime) -> str:
    shift = current_shift(WEEKLY, now)
    assert shift is not None
    return shift.member


def test_the_first_member_is_on_call_from_the_first_handover() -> None:
    shift = current_shift(WEEKLY, at(2026, 3, 23, 9, 0))

    assert shift is not None
    assert (shift.member, shift.index) == ("asha", 0)


def test_nobody_is_on_call_before_the_rotation_starts_or_without_members() -> None:
    assert current_shift(WEEKLY, at(2026, 3, 23, 8, 59)) is None
    assert current_shift(Rotation((), WEEKLY.handover, WEEKLY.time_zone, 7), at(2026, 4, 1)) is None


def test_the_rotation_moves_on_at_each_handover_and_wraps_round() -> None:
    assert who(at(2026, 3, 30, 8, 59)) == "asha"
    assert who(at(2026, 3, 30, 9, 0)) == "ben"
    assert who(at(2026, 4, 13, 9, 0)) == "asha"


def test_the_handover_stays_at_local_nine_across_the_clocks_going_forward() -> None:
    # UK clocks go forward on 2026-03-29, inside the first shift: 08:00 UTC is 09:00 local after.
    shift = current_shift(WEEKLY, datetime(2026, 3, 25, 12, 0, tzinfo=UTC))

    assert shift is not None
    assert shift.ends_at == at(2026, 3, 30, 9, 0)
    assert shift.ends_at.astimezone(UTC).hour == 8
    assert who(datetime(2026, 3, 30, 7, 59, tzinfo=UTC)) == "asha"
    assert who(datetime(2026, 3, 30, 8, 0, tzinfo=UTC)) == "ben"


def test_now_in_any_zone_gives_the_same_answer() -> None:
    kolkata = datetime(2026, 4, 6, 13, 30, tzinfo=ZoneInfo("Asia/Kolkata"))  # 09:00 London

    assert who(kolkata) == "chen"

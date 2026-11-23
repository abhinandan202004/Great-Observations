from datetime import UTC, datetime, timedelta

from infrawatch_core.escalation import Escalation, next_escalation
from infrawatch_core.oncall import Rotation

# Ben is on call (second week of a weekly rotation starting 2026-11-02 09:00 UTC).
ROTATION = Rotation(("asha", "ben", "chen"), datetime(2026, 11, 2, 9, 0), "UTC", 7)
RAISED = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)
TEN = timedelta(minutes=10)


def at(minutes: float) -> datetime:
    return RAISED + timedelta(minutes=minutes)


def test_nothing_is_due_before_the_first_timer() -> None:
    assert next_escalation(ROTATION, RAISED, at(9.9), TEN, done=0) is None


def test_the_first_step_goes_to_the_person_after_the_on_call() -> None:
    assert next_escalation(ROTATION, RAISED, at(10), TEN, done=0) == Escalation(1, "ben", "chen")


def test_each_later_step_waits_its_own_interval_and_wraps_round_the_rotation() -> None:
    assert next_escalation(ROTATION, RAISED, at(15), TEN, done=1) is None
    assert next_escalation(ROTATION, RAISED, at(20), TEN, done=1) == Escalation(2, "ben", "asha")


def test_it_stops_once_everyone_else_has_been_asked() -> None:
    assert next_escalation(ROTATION, RAISED, at(500), TEN, done=2) is None


def test_a_rotation_of_one_or_nobody_on_call_never_escalates() -> None:
    alone = Rotation(("asha",), ROTATION.handover, "UTC", 7)
    not_started = Rotation(ROTATION.members, datetime(2027, 1, 1), "UTC", 7)

    assert next_escalation(alone, RAISED, at(60), TEN, done=0) is None
    assert next_escalation(not_started, RAISED, at(60), TEN, done=0) is None

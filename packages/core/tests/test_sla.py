from datetime import UTC, datetime, timedelta

from infrawatch_core.lifecycle import Status
from infrawatch_core.sla import Policy, timers

S = Status
T0 = datetime(2026, 11, 19, 9, 0, tzinfo=UTC)
P2 = Policy(acknowledge=timedelta(minutes=15), resolve=timedelta(hours=8))


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def test_both_clocks_run_from_raised() -> None:
    ack, resolve = timers([(T0, S.RAISED)], P2, at(10))

    assert (ack.due, ack.remaining, ack.breached) == (at(15), timedelta(minutes=5), False)
    assert resolve.due == at(480)
    assert ack.stopped_at is None


def test_unacknowledged_past_the_target_is_breached_and_overdue() -> None:
    ack, _ = timers([(T0, S.RAISED)], P2, at(20))

    assert ack.breached
    assert ack.remaining == timedelta(minutes=-5)


def test_acknowledging_in_time_stops_the_clock_unbreached() -> None:
    ack, resolve = timers([(T0, S.RAISED), (at(12), S.ACKNOWLEDGED)], P2, at(600))

    assert (ack.stopped_at, ack.remaining, ack.breached) == (at(12), timedelta(minutes=3), False)
    assert resolve.breached  # still open after 10 hours


def test_a_late_acknowledgement_stays_breached() -> None:
    ack, _ = timers([(T0, S.RAISED), (at(30), S.ACKNOWLEDGED)], P2, at(31))

    assert ack.breached


def test_a_regression_to_raised_does_not_restart_the_acknowledge_clock() -> None:
    events = [(T0, S.RAISED), (at(5), S.ACKNOWLEDGED), (at(6), S.RAISED)]

    ack, _ = timers(events, P2, at(60))

    assert ack.stopped_at == at(5)
    assert not ack.breached


def test_resolved_and_closed_stop_the_resolve_clock() -> None:
    events = [(T0, S.RAISED), (at(1), S.ACKNOWLEDGED), (at(100), S.RESOLVED)]

    _, resolve = timers(events, P2, at(1000))
    _, after_close = timers([*events, (at(200), S.CLOSED)], P2, at(1000))

    assert resolve.stopped_at == after_close.stopped_at == at(100)
    assert not resolve.breached


def test_a_reopen_restarts_the_resolve_clock_from_raised() -> None:
    events = [(T0, S.RAISED), (at(100), S.RESOLVED), (at(110), S.INVESTIGATING)]

    _, resolve = timers(events, P2, at(500))

    assert resolve.stopped_at is None
    assert resolve.breached

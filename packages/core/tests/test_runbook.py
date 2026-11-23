from dataclasses import replace
from datetime import UTC, datetime, timedelta

from infrawatch_core.runbook import Runbook, may_close, missing

COMPLETE = Runbook(
    timeline="09:00 detected, 09:05 acknowledged",
    root_cause="A bad deploy disabled the payment retry",
    contributing_factors="No canary",
    remediation="Rolled back; add a canary",
    workaround="Manual retries, removed",
    similar_incidents=("incident-12",),
    none_similar="",
)
RESOLVED = datetime(2026, 11, 24, 10, 0, tzinfo=UTC)


def test_a_complete_runbook_misses_nothing() -> None:
    assert missing(COMPLETE) == []


def test_each_empty_or_blank_field_is_reported() -> None:
    gaps = missing(replace(COMPLETE, timeline="", workaround="   \n"))

    assert gaps == ["timeline", "workaround"]


def test_similar_incidents_needs_links_or_a_statement_that_none_were_found() -> None:
    none_named = replace(COMPLETE, similar_incidents=())

    assert missing(none_named) == ["similar_incidents"]
    assert missing(replace(none_named, none_similar="Searched checkout incidents, 90 days")) == []
    assert missing(replace(none_named, none_similar="  ")) == ["similar_incidents"]


def test_closing_needs_a_version_approved_since_the_latest_resolution() -> None:
    before = RESOLVED - timedelta(minutes=5)
    after = RESOLVED + timedelta(minutes=5)

    assert may_close(RESOLVED, [after])
    assert not may_close(RESOLVED, [])
    assert not may_close(RESOLVED, [before])  # approved for an earlier resolution, then reopened
    assert not may_close(None, [after])  # never resolved

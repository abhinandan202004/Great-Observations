from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast

from sqlalchemy import Row

from infrawatch_worker.mail import message, retry_delay


def row(**overrides: object) -> Row[Any]:
    fields = {
        "idempotency_key": "incident.raised:abc:42",
        "to_addresses": ["payments-team@infrawatch.local"],
        "cc_addresses": ["developer@infrawatch.local"],
        "subject": "[InfraWatch] P2 #7 Raised: Checkout errors",
        "body": "Checkout errors\n",
    }
    return cast(Row[Any], SimpleNamespace(**(fields | overrides)))


def test_retries_back_off_from_thirty_seconds_to_an_hour() -> None:
    assert [retry_delay(n) for n in (1, 2, 3)] == [timedelta(seconds=s) for s in (30, 60, 120)]
    assert retry_delay(20) == timedelta(hours=1)


def test_the_message_carries_group_to_on_call_cc_and_a_stable_id() -> None:
    email = message(row(), "infrawatch@infrawatch.local")

    assert email["To"] == "payments-team@infrawatch.local"
    assert email["Cc"] == "developer@infrawatch.local"
    assert email["Message-ID"] == message(row(), "x@y")["Message-ID"]
    assert email["Message-ID"] != message(row(idempotency_key="other"), "x@y")["Message-ID"]


def test_no_cc_header_when_nobody_is_on_call() -> None:
    assert message(row(cc_addresses=[]), "infrawatch@infrawatch.local")["Cc"] is None

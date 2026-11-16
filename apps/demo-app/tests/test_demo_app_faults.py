import asyncio

import httpx2
import pytest
from fastapi.testclient import TestClient

from infrawatch_demo_app.faults import FaultActiveError, Faults
from infrawatch_demo_app.main import create_app
from infrawatch_demo_app.telemetry import Reporter, sign, summarise


def test_summarise_reports_rate_errors_and_p95() -> None:
    window = [(float(ms), ms != 100) for ms in range(1, 101)]

    assert summarise(window, seconds=5) == {
        "request_rate_per_s": 20.0,
        "error_rate_percent": 1.0,
        "latency_p95_ms": 95.0,
    }
    assert summarise([(40.0, True)], seconds=5)["latency_p95_ms"] == 40.0


def test_summarise_of_an_empty_window_has_no_latency() -> None:
    assert summarise([], seconds=5) == {"request_rate_per_s": 0.0, "error_rate_percent": 0.0}


def test_only_one_fault_runs_at_a_time_and_it_expires() -> None:
    clock = [0.0]
    faults = Faults(clock=lambda: clock[0])

    faults.start("error-burst", minutes=5)
    with pytest.raises(FaultActiveError):
        faults.start("dependency-latency", minutes=5)

    clock[0] = 299.0
    assert faults.active() == "error-burst"
    clock[0] = 300.0
    assert faults.active() is None
    faults.start("dependency-latency", minutes=1)


def test_cpu_spike_starts_burners_and_stop_ends_them() -> None:
    faults = Faults()

    faults.start("cpu-spike", minutes=1)
    burners = faults.burners
    faults.stop()

    assert burners
    assert all(burner.poll() is not None for burner in burners)
    assert faults.active() is None


def test_fault_endpoints_and_checkout_under_error_burst() -> None:
    app = create_app()
    client = TestClient(app)

    assert client.post("/faults/disk-full").status_code == 422
    assert client.post("/faults/error-burst?minutes=0").status_code == 422
    assert client.post("/faults/error-burst").json() == {"active": "error-burst"}
    assert client.post("/faults/cpu-spike").status_code == 409

    statuses = [client.post("/checkout").status_code for _ in range(30)]
    assert set(statuses) == {200, 502}
    assert len(app.state.reporter.window) == 30
    assert all(entry["correlation_id"] for entry in app.state.reporter.logs)

    assert client.delete("/faults").json() == {"active": None}
    assert client.post("/faults/bad-deploy").status_code == 200
    assert [change["kind"] for change in app.state.reporter.changes] == ["deploy"]


def test_flush_signs_changes_and_keeps_data_when_the_api_is_down() -> None:
    reporter = Reporter("webhook-secret")
    reporter.record(40.0, True, "abc")
    reporter.change("deploy", "Deployed checkout v2")
    seen: list[httpx2.Request] = []
    api_up = False

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200 if api_up else 503)

    async def scenario() -> None:
        nonlocal api_up
        async with httpx2.AsyncClient(
            transport=httpx2.MockTransport(handler), base_url="http://api"
        ) as client:
            await reporter.flush(client)
            assert (len(reporter.changes), len(reporter.logs), len(reporter.samples)) == (1, 1, 3)

            api_up = True
            await reporter.flush(client)

    asyncio.run(scenario())

    # The second flush closes an empty window, which adds two more samples before sending.
    assert (len(reporter.changes), len(reporter.logs), len(reporter.samples)) == (0, 0, 0)
    change = next(r for r in seen[1:] if r.url.path == "/ingest/changes")
    assert change.headers["X-Signature-256"] == sign(change.content, "webhook-secret")


def test_request_rate_uses_the_real_window_length() -> None:
    reporter = Reporter("secret")
    for _ in range(50):
        reporter.record(40.0, True, "abc")
    reporter.window_started -= 10  # the window has been open for 10 s, not the nominal 5

    async def scenario() -> None:
        transport = httpx2.MockTransport(lambda request: httpx2.Response(503))
        async with httpx2.AsyncClient(transport=transport, base_url="http://api") as client:
            await reporter.flush(client)

    asyncio.run(scenario())

    rate = next(s["value"] for s in reporter.samples if s["metric"] == "request_rate_per_s")
    assert rate == pytest.approx(5.0, rel=0.05)

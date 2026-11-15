import threading
import time
from pathlib import Path

import httpx2
import pytest

from infrawatch_agent.__main__ import (
    backoff_delay,
    collect_forever,
    deliver_forever,
    flush,
)
from infrawatch_agent.buffer import Buffer, Sample
from infrawatch_agent.collector import Collector


def samples(n: int, start: int = 0) -> list[Sample]:
    return [Sample(f"t{i}", "cpu_percent", float(i)) for i in range(start, start + n)]


def status_error(code: int) -> httpx2.HTTPStatusError:
    request = httpx2.Request("POST", "http://api/ingest/metrics")
    return httpx2.HTTPStatusError(
        "error", request=request, response=httpx2.Response(code, request=request)
    )


def test_buffer_drops_oldest_when_full_and_reports_count(tmp_path: Path) -> None:
    buffer = Buffer(tmp_path / "b.sqlite3", max_samples=5)

    assert buffer.add(samples(3)) == 0
    assert buffer.add(samples(4, start=3)) == 2

    _, kept = buffer.oldest(10)
    assert [s.value for s in kept] == [2.0, 3.0, 4.0, 5.0, 6.0]


def test_buffer_survives_reopen(tmp_path: Path) -> None:
    Buffer(tmp_path / "b.sqlite3").add(samples(3))

    assert len(Buffer(tmp_path / "b.sqlite3")) == 3


@pytest.mark.parametrize("failures", [1, 2, 6, 7, 50])
def test_backoff_stays_between_one_and_sixty_seconds(failures: int) -> None:
    for _ in range(100):
        assert 1.0 <= backoff_delay(failures) <= 60.0
    assert backoff_delay(50) == 60.0


def test_flush_sends_everything_in_order_and_empties_buffer(tmp_path: Path) -> None:
    buffer = Buffer(tmp_path / "b.sqlite3")
    buffer.add(samples(1200))
    sent: list[Sample] = []

    flush(buffer, sent.extend)

    assert sent == samples(1200)
    assert len(buffer) == 0


def test_flush_keeps_samples_when_delivery_fails(tmp_path: Path) -> None:
    buffer = Buffer(tmp_path / "b.sqlite3")
    buffer.add(samples(3))

    def unavailable(batch: list[Sample]) -> None:
        raise status_error(503)

    with pytest.raises(httpx2.HTTPStatusError):
        flush(buffer, unavailable)
    assert len(buffer) == 3


def test_flush_drops_a_batch_the_api_rejects_as_malformed(tmp_path: Path) -> None:
    buffer = Buffer(tmp_path / "b.sqlite3")
    buffer.add(samples(3))

    def malformed(batch: list[Sample]) -> None:
        raise status_error(422)

    flush(buffer, malformed)
    assert len(buffer) == 0


def test_collector_reports_cpu_memory_disk_and_network() -> None:
    metrics = {s.metric for s in Collector().collect()}

    assert metrics == {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "net_sent_bytes_per_s",
        "net_recv_bytes_per_s",
    }


class StopReadingsError(Exception):
    pass


class CountingCollector:
    def __init__(self, readings: int) -> None:
        self.left = readings

    def collect(self) -> list[Sample]:
        if self.left == 0:
            raise StopReadingsError
        self.left -= 1
        return [Sample("t", "cpu_percent", 1.0)]


def test_readings_continue_while_delivery_is_stuck(tmp_path: Path) -> None:
    path = tmp_path / "b.sqlite3"
    stuck = threading.Event()
    release = threading.Event()

    def hanging_post(batch: list[Sample]) -> None:
        stuck.set()
        release.wait(timeout=10)
        raise status_error(503)

    Buffer(path).add(samples(1))
    threading.Thread(target=deliver_forever, args=(path, hanging_post, 60.0), daemon=True).start()
    assert stuck.wait(timeout=5)

    started = time.monotonic()
    with pytest.raises(StopReadingsError):
        collect_forever(CountingCollector(readings=10).collect, Buffer(path), interval=0.01)
    release.set()

    assert time.monotonic() - started < 2
    assert len(Buffer(path)) == 1 + 10 * 2  # each reading adds its sample plus the drop count

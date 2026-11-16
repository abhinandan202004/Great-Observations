"""Entry point: ``python -m infrawatch_agent``.

Collects host metrics every interval into the on-disk buffer and delivers them to the
ingest API, retrying with exponential backoff (ADR 0015). Also serves ``/health``.
"""

import json
import logging
import os
import random
import signal
import sys
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx2

from infrawatch_agent import __version__
from infrawatch_agent.buffer import Buffer, Sample
from infrawatch_agent.collector import Collector

HEALTH_BODY = json.dumps({"status": "ok", "service": "agent", "version": __version__}).encode()
BATCH_SIZE = 500

log = logging.getLogger("infrawatch_agent")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(HEALTH_BODY)))
        self.end_headers()
        self.wfile.write(HEALTH_BODY)


def backoff_delay(failures: int) -> float:
    """Seconds to wait after ``failures`` consecutive failures: 1 s doubling to 60 s, jittered."""
    jitter = random.uniform(1.0, 1.5)  # noqa: S311  # spreads retries, not security-relevant
    return min(60.0, 2.0 ** (failures - 1) * jitter)


def flush(buffer: Buffer, post: Callable[[list[Sample]], None]) -> None:
    """Deliver every buffered sample, oldest first. Raises on a failure worth retrying."""
    while True:
        last_id, batch = buffer.oldest(BATCH_SIZE)
        if not batch:
            return
        try:
            post(batch)
        except httpx2.HTTPStatusError as error:
            if error.response.status_code != 422:
                raise
            # A batch the API rejects as malformed can never succeed; drop it so it
            # does not block everything queued behind it.
            log.error("Dropped %d samples rejected by the API: %s", len(batch), error)
        buffer.remove_through(last_id)


def collect_forever(collect: Callable[[], list[Sample]], buffer: Buffer, interval: float) -> None:
    dropped = 0
    next_at = time.monotonic()
    while True:
        samples = collect()
        samples.append(Sample(samples[0].time, "agent_samples_dropped", float(dropped)))
        dropped = buffer.add(samples)
        if dropped:
            log.warning("Buffer full: dropped the %d oldest samples", dropped)
        next_at = max(next_at + interval, time.monotonic())
        time.sleep(max(0.0, next_at - time.monotonic()))  # the clock moves on after max()


def deliver_forever(
    buffer_path: Path, post: Callable[[list[Sample]], None], interval: float
) -> None:
    """Runs in its own thread so a slow or unreachable API never delays a reading."""
    buffer = Buffer(buffer_path)  # opened here: an sqlite3 connection only works in its own thread
    failures = 0
    while True:
        try:
            flush(buffer, post)
            failures, delay = 0, interval
        except httpx2.HTTPError as error:
            failures += 1
            delay = backoff_delay(failures)
            log.warning("Delivery failed (%s); %d samples buffered", error, len(buffer))
        time.sleep(delay)


def stop_process(args: threading.ExceptHookArgs) -> None:
    """A crashed thread must stop the container, not leave it half-working but healthy."""
    threading.__excepthook__(args)
    os._exit(1)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx2").setLevel(logging.WARNING)  # one INFO line per request otherwise
    url = os.environ.get("INGEST_URL", "http://api:8000") + "/ingest/metrics"
    headers = {"Authorization": f"Bearer {os.environ['INGEST_API_KEY']}"}
    service = os.environ.get("AGENT_SERVICE", "demo-host")
    buffer_path = Path(
        os.environ.get("AGENT_BUFFER_PATH", "/var/lib/infrawatch/agent-buffer.sqlite3")
    )

    def post(samples: list[Sample]) -> None:
        body = {"service": service, "samples": [s._asdict() for s in samples]}
        httpx2.post(url, json=body, headers=headers, timeout=10).raise_for_status()

    interval = float(os.environ.get("AGENT_INTERVAL_SECONDS", "5"))
    port = int(os.environ.get("HEALTH_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)  # noqa: S104  # container listens on all interfaces

    threading.excepthook = stop_process
    threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(
        target=deliver_forever, args=(buffer_path, post, interval), daemon=True
    ).start()

    # PID 1 in a container gets no default SIGTERM handling; exit cleanly so cleanup code runs.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    collect_forever(Collector().collect, Buffer(buffer_path), interval)


if __name__ == "__main__":
    main()

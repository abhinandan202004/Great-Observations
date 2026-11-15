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


def run(
    collector: Collector, buffer: Buffer, post: Callable[[list[Sample]], None], interval: float
) -> None:
    next_collect = next_send = time.monotonic()
    failures = dropped = 0
    while True:
        now = time.monotonic()
        if now >= next_collect:
            samples = collector.collect()
            samples.append(Sample(samples[0].time, "agent_samples_dropped", float(dropped)))
            dropped = buffer.add(samples)
            if dropped:
                log.warning("Buffer full: dropped the %d oldest samples", dropped)
            next_collect = now + interval
        if now >= next_send:
            try:
                flush(buffer, post)
                failures = 0
                next_send = next_collect
            except httpx2.HTTPError as error:
                failures += 1
                next_send = now + backoff_delay(failures)
                log.warning("Delivery failed (%s); %d samples buffered", error, len(buffer))
        time.sleep(max(0.0, min(next_collect, next_send) - time.monotonic()))


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

    port = int(os.environ.get("HEALTH_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)  # noqa: S104  # container listens on all interfaces
    threading.Thread(target=server.serve_forever, daemon=True).start()

    # PID 1 in a container gets no default SIGTERM handling; exit cleanly so cleanup code runs.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    run(
        Collector(), Buffer(buffer_path), post, float(os.environ.get("AGENT_INTERVAL_SECONDS", "5"))
    )


if __name__ == "__main__":
    main()

"""Collects the demo app's request metrics, logs and change events and posts them to the API.

shortcut: unsent telemetry waits in bounded in-memory queues (about 28 minutes of metrics,
3 minutes of logs) and is lost on restart; use an on-disk buffer like the agent's if the
demo app's own data ever has to survive one.
"""

import hashlib
import hmac
import json
import logging
import math
import time
from collections import deque
from datetime import UTC, datetime
from itertools import islice
from uuid import uuid4

import httpx2

SERVICE = "checkout"
BATCH_SIZE = 500

log = logging.getLogger("infrawatch_demo_app")


def summarise(window: list[tuple[float, bool]], seconds: float) -> dict[str, float]:
    """Request rate, error rate and p95 latency for one window of (latency_ms, ok) results."""
    if not window:
        return {"request_rate_per_s": 0.0, "error_rate_percent": 0.0}
    latencies = sorted(latency for latency, _ in window)
    errors = sum(1 for _, ok in window if not ok)
    return {
        "request_rate_per_s": len(window) / seconds,
        "error_rate_percent": 100 * errors / len(window),
        "latency_p95_ms": latencies[math.ceil(0.95 * len(latencies)) - 1],
    }


def sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def now() -> str:
    return datetime.now(UTC).isoformat()


class Reporter:
    def __init__(self, webhook_secret: str) -> None:
        self.webhook_secret = webhook_secret
        self.window: list[tuple[float, bool]] = []
        self.window_started = time.monotonic()
        self.samples: deque[dict[str, object]] = deque(maxlen=1000)
        self.logs: deque[dict[str, object]] = deque(maxlen=5000)
        self.changes: deque[dict[str, object]] = deque(maxlen=100)

    def record(self, latency_ms: float, ok: bool, correlation_id: str) -> None:
        self.window.append((latency_ms, ok))
        if not ok:
            level, message = "error", "checkout failed: payment-gateway returned an error"
        elif latency_ms > 500:
            level, message = "warning", f"checkout slow: payment-gateway took {latency_ms:.0f} ms"
        else:
            level, message = "info", f"checkout completed in {latency_ms:.0f} ms"
        self.logs.append(
            {
                "id": str(uuid4()),
                "time": now(),
                "level": level,
                "message": message,
                "correlation_id": correlation_id,
            }
        )

    def change(self, kind: str, summary: str) -> None:
        self.changes.append(
            {
                "id": str(uuid4()),
                "time": now(),
                "service": SERVICE,
                "kind": kind,
                "summary": summary,
            }
        )

    async def flush(self, client: httpx2.AsyncClient) -> None:
        """Close the current window and deliver everything queued, oldest first."""
        # Measured, not assumed: a slow delivery makes the next window longer than the interval.
        ended = time.monotonic()
        seconds = max(ended - self.window_started, 0.001)
        window, self.window, self.window_started = self.window, [], ended
        sampled_at = now()
        self.samples.extend(
            {"time": sampled_at, "metric": metric, "value": value}
            for metric, value in summarise(window, seconds).items()
        )
        try:
            while self.changes:
                body = json.dumps(self.changes[0]).encode()
                headers = {
                    "X-Signature-256": sign(body, self.webhook_secret),
                    "Content-Type": "application/json",
                }
                await self._post(client, "/ingest/changes", content=body, headers=headers)
                self.changes.popleft()
            for path, field, queue in (
                ("/ingest/metrics", "samples", self.samples),
                ("/ingest/logs", "entries", self.logs),
            ):
                while queue:
                    batch = list(islice(queue, BATCH_SIZE))
                    await self._post(client, path, json={"service": SERVICE, field: batch})
                    for _ in batch:
                        queue.popleft()
        except httpx2.HTTPError as error:
            log.warning("Delivery failed (%s); will retry with the next window", error)

    @staticmethod
    async def _post(client: httpx2.AsyncClient, path: str, **kwargs: object) -> None:
        """Post once. Raises on a failure worth retrying."""
        response = await client.post(path, **kwargs)  # type: ignore[arg-type]
        if response.status_code == 422:
            # Malformed data can never succeed; drop it so it does not block the queue.
            log.error("Dropped data rejected by the API on %s: %s", path, response.text[:300])
            return
        response.raise_for_status()

"""Entry point: ``python -m infrawatch_worker``: the health endpoint and the periodic jobs."""

import asyncio
import json
import logging
import os
import signal
import sys
import threading
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from infrawatch_worker import __version__
from infrawatch_worker.alerts import evaluate
from infrawatch_worker.mail import deliver, smtp_sender

Job = Callable[[AsyncConnection], Awaitable[int]]

log = logging.getLogger("infrawatch_worker")

HEALTH_BODY = json.dumps({"status": "ok", "service": "worker", "version": __version__}).encode()


class HealthHandler(BaseHTTPRequestHandler):
    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        pass  # suppress healthcheck noise in container logs

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(HEALTH_BODY)))
        self.end_headers()
        self.wfile.write(HEALTH_BODY)


async def periodic(engine: AsyncEngine, every: float, job: Job, done: str) -> None:
    """Run ``job`` in its own transaction every ``every`` seconds, logging what it did."""
    while True:
        try:
            async with engine.begin() as conn:
                count = await job(conn)
            if count:
                log.info("%s: %d", done, count)
        except Exception:
            # One bad pass (database restarting, say) must not stop the job for good.
            log.exception("%s failed; retrying", done)
        await asyncio.sleep(every)


async def run(database_url: str) -> None:
    engine = create_async_engine(database_url)
    send, sender = smtp_sender(), os.environ.get("MAIL_FROM", "infrawatch@infrawatch.local")
    await asyncio.gather(
        periodic(
            engine,
            float(os.environ.get("ALERT_EVAL_SECONDS", "15")),
            lambda conn: evaluate(conn, datetime.now(UTC)),
            "alert drafts created",
        ),
        periodic(
            engine,
            float(os.environ.get("MAIL_POLL_SECONDS", "5")),
            lambda conn: deliver(conn, send, sender),
            "emails sent",
        ),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    port = int(os.environ.get("HEALTH_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)  # noqa: S104  # container listens on all interfaces
    # PID 1 in a container gets no default SIGTERM handling; exit cleanly so cleanup code runs.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    asyncio.run(run(os.environ["DATABASE_URL"]))


if __name__ == "__main__":
    main()

"""Entry point: ``python -m infrawatch_worker``: the health endpoint plus the alert loop."""

import asyncio
import json
import logging
import os
import signal
import sys
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from sqlalchemy.ext.asyncio import create_async_engine

from infrawatch_worker import __version__
from infrawatch_worker.alerts import evaluate

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


async def alert_loop(database_url: str, every: float) -> None:
    engine = create_async_engine(database_url)
    while True:
        try:
            async with engine.begin() as conn:
                created = await evaluate(conn, datetime.now(UTC))
            if created:
                log.info("created %d alert draft(s)", created)
        except Exception:
            # One bad pass (database restarting, say) must not stop alerting for good.
            log.exception("alert evaluation failed; retrying")
        await asyncio.sleep(every)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    port = int(os.environ.get("HEALTH_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)  # noqa: S104  # container listens on all interfaces
    # PID 1 in a container gets no default SIGTERM handling; exit cleanly so cleanup code runs.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    every = float(os.environ.get("ALERT_EVAL_SECONDS", "15"))
    asyncio.run(alert_loop(os.environ["DATABASE_URL"], every))


if __name__ == "__main__":
    main()

"""Entry point: ``python -m infrawatch_agent``.

Until the collection loop lands, the process only serves its health endpoint.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from infrawatch_agent import __version__

HEALTH_BODY = json.dumps({"status": "ok", "service": "agent", "version": __version__}).encode()


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


def main() -> None:
    port = int(os.environ.get("HEALTH_PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)  # noqa: S104  # container listens on all interfaces
    server.serve_forever()


if __name__ == "__main__":
    main()

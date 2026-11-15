import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from http.server import ThreadingHTTPServer

import pytest

from infrawatch_agent import __version__
from infrawatch_agent.__main__ import HealthHandler


@pytest.fixture
def base_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def test_health_reports_ok(base_url: str) -> None:
    with urllib.request.urlopen(f"{base_url}/health") as response:
        assert json.load(response) == {"status": "ok", "service": "agent", "version": __version__}


def test_unknown_path_is_not_found(base_url: str) -> None:
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(f"{base_url}/other")
    assert error.value.code == 404

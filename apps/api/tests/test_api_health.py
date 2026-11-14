from fastapi.testclient import TestClient

from infrawatch_api import __version__
from infrawatch_api.main import create_app


def test_health_reports_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api", "version": __version__}

from fastapi.testclient import TestClient

from infrawatch_demo_app import __version__
from infrawatch_demo_app.main import create_app


def test_health_reports_ok() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "demo-app", "version": __version__}

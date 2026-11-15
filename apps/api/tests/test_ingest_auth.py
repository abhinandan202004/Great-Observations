from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from infrawatch_api.main import create_app

BATCH = {
    "service": "demo-host",
    "samples": [{"time": datetime.now(UTC).isoformat(), "metric": "cpu_percent", "value": 1.0}],
}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("INGEST_API_KEYS", "first-key,second-key")
    return TestClient(create_app())


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer wrong-key"}, {"Authorization": "Basic first-key"}],
)
def test_ingest_rejects_missing_or_wrong_key(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post("/ingest/metrics", json=BATCH, headers=headers)

    assert response.status_code == 401


def test_ingest_rejects_everything_when_no_keys_are_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("INGEST_API_KEYS", raising=False)
    response = TestClient(create_app()).post(
        "/ingest/metrics", json=BATCH, headers={"Authorization": "Bearer "}
    )

    assert response.status_code == 401


def test_ingest_rejects_naive_timestamps_and_nan(client: TestClient) -> None:
    headers = {"Authorization": "Bearer second-key"}
    naive = {**BATCH, "samples": [{"time": "2026-11-16T10:00:00", "metric": "m", "value": 1}]}
    nan = {**BATCH, "samples": [{**BATCH["samples"][0], "value": "NaN"}]}  # type: ignore[dict-item]

    assert client.post("/ingest/metrics", json=naive, headers=headers).status_code == 422
    assert client.post("/ingest/metrics", json=nan, headers=headers).status_code == 422

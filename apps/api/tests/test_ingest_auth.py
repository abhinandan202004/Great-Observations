import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from infrawatch_api.main import create_app

NOW = datetime.now(UTC).isoformat()
BATCH = {
    "service": "demo-host",
    "samples": [{"time": NOW, "metric": "cpu_percent", "value": 1.0}],
}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("INGEST_API_KEYS", "first-key,second-key")
    monkeypatch.setenv("CHANGE_WEBHOOK_SECRET", "webhook-secret")
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


def test_log_ingest_requires_a_key_and_a_known_level(client: TestClient) -> None:
    entry = {"id": "0b0e7a52-6f0b-4c1d-9a55-0d3f1f6f8a11", "time": NOW, "message": "m"}
    batch = {"service": "checkout", "entries": [{**entry, "level": "fatal"}]}
    headers = {"Authorization": "Bearer first-key"}

    assert client.post("/ingest/logs", json=batch).status_code == 401
    assert client.post("/ingest/logs", json=batch, headers=headers).status_code == 422


def signed(body: bytes, secret: str) -> dict[str, str]:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return {"X-Signature-256": f"sha256={digest}", "Content-Type": "application/json"}


CHANGE = {
    "id": "5f0c1f3e-58a9-4b62-8f0e-3a5d2c7b9e10",
    "time": NOW,
    "service": "checkout",
    "kind": "deploy",
    "summary": "Deployed checkout v2",
}


@pytest.mark.parametrize("secret", ["wrong-secret", ""])
def test_change_webhook_rejects_a_bad_signature(client: TestClient, secret: str) -> None:
    body = json.dumps(CHANGE).encode()

    assert client.post("/ingest/changes", content=body).status_code == 401
    response = client.post("/ingest/changes", content=body, headers=signed(body, secret))
    assert response.status_code == 401


def test_change_webhook_rejects_a_body_changed_after_signing(client: TestClient) -> None:
    headers = signed(json.dumps(CHANGE).encode(), "webhook-secret")
    tampered = json.dumps({**CHANGE, "summary": "Deployed something else"}).encode()

    assert client.post("/ingest/changes", content=tampered, headers=headers).status_code == 401


def test_change_webhook_rejects_everything_when_no_secret_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHANGE_WEBHOOK_SECRET", raising=False)
    body = json.dumps(CHANGE).encode()

    response = TestClient(create_app()).post(
        "/ingest/changes", content=body, headers=signed(body, "")
    )
    assert response.status_code == 401


def test_change_webhook_validates_a_correctly_signed_body(client: TestClient) -> None:
    body = json.dumps({**CHANGE, "kind": "reboot"}).encode()

    response = client.post("/ingest/changes", content=body, headers=signed(body, "webhook-secret"))
    assert response.status_code == 422


@pytest.mark.parametrize(
    "query",
    [
        "",  # a time range is required, so a search never scans all 30 days by accident
        "since=2026-11-16T10:00:00",  # no time zone
        "since=2026-11-16T10:00:00Z&level=fatal",
        "since=2026-11-16T10:00:00Z&limit=0",
        "since=2026-11-16T10:00:00Z&limit=1001",
    ],
)
def test_log_search_rejects_bad_filters(client: TestClient, query: str) -> None:
    assert client.get(f"/logs?{query}").status_code == 422

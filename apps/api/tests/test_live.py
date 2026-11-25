from typing import Any, cast

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from infrawatch_api import live
from infrawatch_api.main import create_app

INCIDENT = "5f0c3a7e-1b2d-4c5e-9f00-0123456789ab"


def event(seq: int, event_id: int | None = None) -> dict[str, Any]:
    return {"incident": INCIDENT, "seq": seq, "id": event_id or seq, "kind": "status"}


def client(**subscriptions: int) -> live.Client:
    c = live.Client(cast(WebSocket, None))
    for target, last in subscriptions.items():
        c.subscriptions[INCIDENT if target == "incident" else live.ALL] = live.Subscription(
            last=last, replaying=False
        )
    return c


def sent(c: live.Client) -> list[dict[str, Any]]:
    return [c.queue.get_nowait() for _ in range(c.queue.qsize())]


def test_a_subscriber_gets_each_new_event_once_and_skips_ones_it_has() -> None:
    c = client(incident=3, all=3)

    assert c.deliver(event(3))
    assert c.deliver(event(4))

    assert [m["seq"] for m in sent(c)] == [4]


def test_events_arriving_during_a_replay_wait_for_it() -> None:
    c = client()
    c.subscriptions[INCIDENT] = live.Subscription()

    c.deliver(event(7))

    assert sent(c) == []
    assert c.subscriptions[INCIDENT].pending == [event(7)]


def test_an_overflowing_queue_reports_failure_so_the_hub_can_drop_the_client() -> None:
    c = client(incident=0)

    assert all(c.deliver(event(seq)) for seq in range(1, live.QUEUE_SIZE + 1))
    assert not c.deliver(event(live.QUEUE_SIZE + 1))


@pytest.fixture
def app_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WEB_URL", "http://localhost:3001")
    monkeypatch.setenv("JWT_SECRET", "x" * 40)
    return TestClient(create_app())


def test_a_foreign_origin_is_refused_before_the_handshake(app_client: TestClient) -> None:
    with (
        pytest.raises(WebSocketDisconnect) as refused,
        app_client.websocket_connect("/ws", headers={"origin": "https://evil.example"}),
    ):
        pass

    assert refused.value.code == live.POLICY


def test_a_bad_token_closes_the_connection(app_client: TestClient) -> None:
    with app_client.websocket_connect("/ws", headers={"origin": "http://localhost:3001"}) as ws:
        ws.send_json({"type": "auth", "token": "not-a-jwt"})
        with pytest.raises(WebSocketDisconnect) as closed:
            ws.receive_json()

    assert closed.value.code == live.UNAUTHENTICATED

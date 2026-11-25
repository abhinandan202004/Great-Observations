"""G3.9 against the running stack: live incident updates over WebSocket.

Run inside the API container, which has the websockets package:
    docker compose exec -T api python - < scripts/check-live.py

Checks: a foreign origin and a missing sign-in are refused; subscribers get each change in order,
including status-only roles and the all-incidents list; after a dropped connection the missed
events are replayed in order; a gap larger than the replay window asks for a refetch; the server
sends heartbeats; and the same works through the web app's /api proxy, as a browser uses it.
"""

import asyncio
import json
import os
import sys
import urllib.request
from typing import Any

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

API = "http://localhost:8000"
WS = "ws://localhost:8000/ws"
PROXIED = "ws://web:3000/api/ws"  # the web container, as the browser reaches the gateway
ORIGIN = os.environ.get("WEB_URL", "http://localhost:3000")
PASSWORD = os.environ["DEMO_USER_PASSWORD"]


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def call(method: str, path: str, token: str | None = None, body: object = None) -> Any:
    request = urllib.request.Request(  # noqa: S310  # fixed local URL
        API + path,
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}
        | ({"Authorization": f"Bearer {token}"} if token else {}),
    )
    with urllib.request.urlopen(request) as response:  # noqa: S310
        return json.loads(response.read() or "null")


def token(user: str) -> str:
    body = {"email": f"{user}@infrawatch.local", "password": PASSWORD}
    return str(call("POST", "/auth/login", body=body)["access_token"])


async def receive(ws: ClientConnection, kind: str, seconds: float = 5) -> dict[str, Any]:
    """The next message of this type, skipping heartbeats."""
    while True:
        message: dict[str, Any] = json.loads(await asyncio.wait_for(ws.recv(), seconds))
        if message["type"] == "ping" and kind != "ping":
            continue
        if message["type"] != kind:
            fail(f"expected {kind}, got {message}")
        return message


async def watch(
    user_token: str, target: str, after: int | None = None, url: str = WS
) -> ClientConnection:
    ws = await connect(url, origin=ORIGIN)  # type: ignore[arg-type]
    await ws.send(json.dumps({"type": "auth", "token": user_token}))
    await ws.send(json.dumps({"type": "subscribe", "target": target, "after": after}))
    return ws


async def main() -> None:
    support, developer, stakeholder = token("support"), token("developer"), token("stakeholder")
    raise_body = {
        "title": "Live check",
        "impact": "Checkout slow",
        "description": "x",
        "severity": "P3",
        "service": "checkout",
    }
    incident = call("POST", "/incidents", support, raise_body)["id"]
    payments = next(
        t["id"] for t in call("GET", "/teams", developer) if t["name"] == "Payments Platform"
    )
    step = 0

    def change() -> None:
        nonlocal step
        step += 1
        call(
            "POST",
            f"/incidents/{incident}/teams/{payments}/checklist",
            developer,
            {"text": f"Step {step}"},
        )

    print("A foreign origin is refused, and so is a connection that never signs in")
    try:
        await connect(WS, origin="https://evil.example")  # type: ignore[arg-type]
        fail("a foreign origin was accepted")
    except InvalidStatus as refused:
        if refused.response.status_code != 403:
            fail(f"a foreign origin got {refused.response.status_code}, expected 403")
    silent = await connect(WS, origin=ORIGIN)  # type: ignore[arg-type]
    try:
        await asyncio.wait_for(silent.recv(), 10)
        fail("a connection without sign-in was served")
    except ConnectionClosed as closed:
        if closed.rcvd is None or closed.rcvd.code != 4401:
            fail(f"an unsigned connection closed with {closed.rcvd}, expected 4401")

    print(
        "G3.9: every open view gets each change, in order, including status-only roles and the list"
    )
    dev_ws = await watch(developer, incident)
    cursor = (await receive(dev_ws, "subscribed"))["cursor"]
    viewer_ws = await watch(stakeholder, incident)
    await receive(viewer_ws, "subscribed")
    list_ws = await watch(developer, "*")
    await receive(list_ws, "subscribed")
    call("POST", f"/incidents/{incident}/status", developer, {"status": "acknowledged"})
    for ws in (dev_ws, viewer_ws):
        event = await receive(ws, "event")
        if (event["incident"], event["seq"], event["kind"]) != (incident, cursor + 1, "status"):
            fail(f"unexpected event {event}")
    if (await receive(list_ws, "event"))["incident"] != incident:
        fail("the all-incidents subscription missed the change")
    cursor += 1
    await viewer_ws.close()
    await list_ws.close()

    print("After a dropped connection the missed events are replayed in order")
    await dev_ws.close()
    change()
    change()
    dev_ws = await watch(developer, incident, cursor)
    seqs = [(await receive(dev_ws, "event"))["seq"] for _ in range(2)]
    if seqs != [cursor + 1, cursor + 2]:
        fail(f"replayed {seqs}, expected {[cursor + 1, cursor + 2]}")
    if (await receive(dev_ws, "subscribed"))["cursor"] != cursor + 2:
        fail("the replay did not end at the latest event")
    await dev_ws.close()

    print("A gap larger than the replay window asks for a refetch")
    behind = cursor + 2
    for _ in range(101):
        change()
    dev_ws = await watch(developer, incident, behind)
    if (await receive(dev_ws, "refetch"))["target"] != incident:
        fail("no refetch for a gap of 101 events")
    await receive(dev_ws, "subscribed")

    print("The server sends a heartbeat every 20 seconds")
    await receive(dev_ws, "ping", seconds=25)
    await dev_ws.send(json.dumps({"type": "pong"}))
    await dev_ws.close()

    print("The same works through the web app's /api proxy")
    proxied = await watch(developer, incident, url=PROXIED)
    await receive(proxied, "subscribed")
    change()
    await receive(proxied, "event")
    await proxied.close()

    print(
        "live: origin and sign-in enforced, changes fan out in order, drops replay, "
        "large gaps refetch, heartbeats flow, and the proxy carries it"
    )


asyncio.run(main())

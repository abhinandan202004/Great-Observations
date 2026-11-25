"""Live incident updates over WebSocket (ADR 0009), fed by LISTEN/NOTIFY (ADR 0010).

The channel carries pointers only: which incident changed, its sequence number and what kind of
change it was. Pages refetch through the REST API, where every permission check still applies.

Protocol, as JSON messages:
  client -> {"type": "auth", "token": ...}            first, within AUTH_TIMEOUT seconds
  client -> {"type": "subscribe", "target": <incident id or "*">, "after": <cursor or null>}
  client -> {"type": "pong"}                           answers each ping
  server -> {"type": "subscribed", "target", "cursor"} after any replay
  server -> {"type": "event", "incident", "seq", "id", "kind"}
  server -> {"type": "refetch", "target"}              the gap was too large to replay
  server -> {"type": "ping"}                           every HEARTBEAT seconds
The cursor is the incident's ``seq`` for one incident, and the global event ``id`` for "*".
"""

import asyncio
import contextlib
import logging
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

import asyncpg
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from infrawatch_api import access
from infrawatch_api.auth import read_access_token
from infrawatch_api.events import CHANNEL
from infrawatch_core.policy import Capability, allows

router = APIRouter()
log = logging.getLogger("infrawatch_api.live")

ALL = "*"
QUEUE_SIZE = 100
REPLAY_WINDOW = 100
HEARTBEAT = 20.0
AUTH_TIMEOUT = 5.0
IDLE_TIMEOUT = 60.0  # three missed heartbeats
POLICY = 1008
UNAUTHENTICATED = 4401
FORBIDDEN = 4403
RESYNC = 4409  # the client fell behind: reconnect and refetch

Event = dict[str, Any]
_EVENTS = "SELECT id, incident_id, seq, kind FROM incident_events "
REPLAY = {
    "id": _EVENTS + "WHERE id > :after AND id <= :current ORDER BY id LIMIT :limit",
    "seq": _EVENTS + "WHERE incident_id = :incident AND seq > :after AND seq <= :current "
    "ORDER BY seq LIMIT :limit",
}


@dataclass
class Subscription:
    last: int = 0
    replaying: bool = True
    pending: list[Event] = field(default_factory=list)


class Client:
    """One connection: what it watches, and a bounded queue of messages waiting to be sent."""

    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.queue: asyncio.Queue[Event] = asyncio.Queue(QUEUE_SIZE)
        self.subscriptions: dict[str, Subscription] = {}

    def offer(self, message: Event) -> bool:
        try:
            self.queue.put_nowait(message)
        except asyncio.QueueFull:
            return False
        return True

    def deliver(self, event: Event) -> bool:
        """Queue the event once if any subscription wants it; False if the queue overflowed."""
        wanted = False
        for target, cursor in ((event["incident"], event["seq"]), (ALL, event["id"])):
            sub = self.subscriptions.get(target)
            if sub is None:
                continue
            if sub.replaying:
                sub.pending.append(event)
            elif cursor > sub.last:
                sub.last = cursor
                wanted = True
        return self.offer({"type": "event", **event}) if wanted else True


class Hub:
    """Every open connection, fed in commit order from one LISTEN connection."""

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.clients: set[Client] = set()
        self.closing: set[asyncio.Task[None]] = set()

    async def run(self, dsn: str) -> None:
        ids: asyncio.Queue[int] = asyncio.Queue()
        fanout = asyncio.create_task(self._fanout(ids))
        try:
            while True:
                lost = asyncio.Event()
                try:
                    conn = await asyncpg.connect(dsn)
                    conn.add_termination_listener(lambda _conn, lost=lost: lost.set())
                    await conn.add_listener(CHANNEL, lambda *args: ids.put_nowait(int(args[3])))
                    await lost.wait()
                except (OSError, asyncpg.PostgresError):
                    log.exception("live updates lost their database connection")
                # Notifications may have been missed: everyone reconnects and replays.
                for client in list(self.clients):
                    self.drop(client)
                await asyncio.sleep(1)
        finally:
            fanout.cancel()

    async def _fanout(self, ids: asyncio.Queue[int]) -> None:
        while True:
            event_id = await ids.get()
            async with self.engine.connect() as conn:
                row = (
                    await conn.execute(
                        text(
                            "SELECT id, incident_id, seq, kind FROM incident_events WHERE id = :id"
                        ),
                        {"id": event_id},
                    )
                ).one()
            event = {
                "incident": str(row.incident_id),
                "seq": row.seq,
                "id": row.id,
                "kind": row.kind,
            }
            for client in list(self.clients):
                if not client.deliver(event):
                    self.drop(client)

    def drop(self, client: Client) -> None:
        self.clients.discard(client)
        task = asyncio.create_task(_close(client.websocket, RESYNC))
        # Keep a reference until it finishes, or the loop may collect the task mid-close.
        self.closing.add(task)
        task.add_done_callback(self.closing.discard)


async def _close(websocket: WebSocket, code: int) -> None:
    with contextlib.suppress(RuntimeError, WebSocketDisconnect):
        await websocket.close(code)


def allowed_origins() -> set[str]:
    web = urlsplit(os.environ.get("WEB_URL", "http://localhost:3000"))
    return {f"{web.scheme}://{web.netloc}"}


async def _subscribe(engine: AsyncEngine, client: Client, target: str, after: Any) -> None:
    sub = client.subscriptions[target] = Subscription()
    cursor = "id" if target == ALL else "seq"
    async with engine.connect() as conn:
        if target == ALL:
            current = await conn.scalar(text("SELECT coalesce(max(id), 0) FROM incident_events"))
        else:
            current = await conn.scalar(
                text("SELECT event_seq FROM incidents WHERE id = :id"), {"id": UUID(target)}
            )
        if current is None:
            del client.subscriptions[target]
            client.offer({"type": "error", "detail": "No such incident"})
            return
        missed: Sequence[Any] = []
        if isinstance(after, int) and after <= current:
            missed = (
                await conn.execute(
                    text(REPLAY[cursor]),
                    {
                        "incident": None if target == ALL else UUID(target),
                        "after": after,
                        "current": current,
                        "limit": REPLAY_WINDOW + 1,
                    },
                )
            ).all()
    if after is not None and (
        not isinstance(after, int) or after > current or len(missed) > REPLAY_WINDOW
    ):
        client.offer({"type": "refetch", "target": target})
        missed = []
    for row in missed:
        event = {"incident": str(row.incident_id), "seq": row.seq, "id": row.id, "kind": row.kind}
        client.offer({"type": "event", **event})
    sub.last = current
    client.offer({"type": "subscribed", "target": target, "cursor": current})
    # Events that arrived while replaying, newer than the replay, go out in order now.
    sub.replaying = False
    for event in sub.pending:
        if event[cursor] > sub.last:
            sub.last = event[cursor]
            client.offer({"type": "event", **event})
    sub.pending.clear()


async def _send(client: Client) -> None:
    with contextlib.suppress(RuntimeError, WebSocketDisconnect):
        while True:
            try:
                message = await asyncio.wait_for(client.queue.get(), HEARTBEAT)
            except TimeoutError:
                message = {"type": "ping"}
            await client.websocket.send_json(message)


@router.websocket("/ws")
async def gateway(websocket: WebSocket) -> None:
    # Browsers attach cookies to WebSocket handshakes and CORS does not apply, so the page's
    # origin is checked before anything else (security guide, section 1.6).
    if websocket.headers.get("origin") not in allowed_origins():
        await websocket.close(POLICY)
        return
    await websocket.accept()
    try:
        # The token comes in the first message, never in the URL, where logs would keep it.
        hello = await asyncio.wait_for(websocket.receive_json(), AUTH_TIMEOUT)
        user = read_access_token(str(hello.get("token", "")), websocket.app.state.jwt_secret)
    except (TimeoutError, ValueError, AttributeError, jwt.PyJWTError, WebSocketDisconnect):
        # shortcut: a connection outlives its 15-minute token; close it at expiry if roles can
        # change mid-session in a way that matters (events carry no incident data today).
        await _close(websocket, UNAUTHENTICATED)
        return
    if not allows(await access.load_roles(websocket, user), Capability.VIEW_INCIDENT_STATUS):
        await _close(websocket, FORBIDDEN)
        return
    hub: Hub = websocket.app.state.hub
    client = Client(websocket)
    hub.clients.add(client)
    sender = asyncio.create_task(_send(client))
    try:
        while True:
            message = await asyncio.wait_for(websocket.receive_json(), IDLE_TIMEOUT)
            if message.get("type") == "subscribe":
                target = str(message.get("target", ""))
                try:
                    if target != ALL:
                        UUID(target)
                except ValueError:
                    client.offer({"type": "error", "detail": "Unknown subscription target"})
                    continue
                await _subscribe(hub.engine, client, target, message.get("after"))
    except (TimeoutError, WebSocketDisconnect, ValueError):
        pass
    finally:
        hub.clients.discard(client)
        sender.cancel()
        await _close(websocket, 1000)

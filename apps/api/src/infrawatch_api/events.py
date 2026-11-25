"""Incident events: appended in the changing transaction, announced to the gateway on commit."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

CHANNEL = "incident_events"
# The worker writes the same rows with the same SQL (infrawatch_worker.events).
APPEND = (
    "WITH bumped AS (UPDATE incidents SET event_seq = event_seq + 1 WHERE id = :id "
    "RETURNING id, event_seq) INSERT INTO incident_events (incident_id, seq, kind) "
    "SELECT id, event_seq, :kind FROM bumped RETURNING id"
)


async def publish(conn: AsyncConnection, incident_id: UUID, kind: str) -> None:
    """Record that the incident changed; NOTIFY carries only a pointer and fires on commit."""
    event_id = await conn.scalar(text(APPEND), {"id": incident_id, "kind": kind})
    await conn.execute(
        text("SELECT pg_notify(:channel, :id)"), {"channel": CHANNEL, "id": str(event_id)}
    )

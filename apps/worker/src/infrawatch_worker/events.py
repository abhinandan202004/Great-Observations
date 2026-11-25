"""Incident events from the worker, in the same form as the API's (infrawatch_api.events)."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

APPEND = (
    "WITH bumped AS (UPDATE incidents SET event_seq = event_seq + 1 WHERE id = :id "
    "RETURNING id, event_seq) INSERT INTO incident_events (incident_id, seq, kind) "
    "SELECT id, event_seq, :kind FROM bumped RETURNING id"
)


async def publish(conn: AsyncConnection, incident_id: UUID, kind: str) -> None:
    event_id = await conn.scalar(text(APPEND), {"id": incident_id, "kind": kind})
    await conn.execute(text("SELECT pg_notify('incident_events', :id)"), {"id": str(event_id)})

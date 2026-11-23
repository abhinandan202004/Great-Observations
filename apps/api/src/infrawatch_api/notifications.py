"""Incident email, queued in the outbox in the same transaction as the change that causes it.

One email per event, to the group addresses of the involved teams with their on-call engineers
in CC. The worker delivers it, so a mail outage never blocks the incident workflow.
"""

import os
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api.oncall import on_call_now

EVENTS = {
    "raised": "Raised",
    "severity": "Severity changed",
    "team_added": "Your team was added",
    "resolved": "Resolved",
    "closed": "Closed",
}
QUEUE = (
    "INSERT INTO outbox (idempotency_key, kind, incident_id, to_addresses, cc_addresses, "
    "subject, body) VALUES (:key || ':' || txid_current(), :kind, :incident, "
    "CAST(:to AS text[]), CAST(:cc AS text[]), :subject, :body)"
)


async def notify(
    conn: AsyncConnection, incident_id: UUID, event: str, team_ids: Sequence[UUID] | None = None
) -> None:
    """Queue the email for one incident event; ``team_ids`` narrows it to those teams."""
    incident = (
        await conn.execute(
            text(
                "SELECT i.number, i.title, i.impact, i.severity, i.status, s.name AS service "
                "FROM incidents i JOIN services s ON s.id = i.service_id WHERE i.id = :id"
            ),
            {"id": incident_id},
        )
    ).one()
    teams = (
        await conn.execute(
            text(
                "SELECT t.id, t.name, t.group_email FROM team_tasks tt "
                "JOIN teams t ON t.id = tt.team_id WHERE tt.incident_id = :id "
                "AND (CAST(:only AS uuid[]) IS NULL OR t.id = ANY(CAST(:only AS uuid[]))) "
                "ORDER BY t.name"
            ),
            {"id": incident_id, "only": list(team_ids) if team_ids is not None else None},
        )
    ).all()
    on_call = await on_call_now(conn, [t.id for t in teams], datetime.now(UTC))
    web = os.environ.get("WEB_URL", "http://localhost:3000")
    title = f"{incident.severity} #{incident.number} {EVENTS[event]}: {incident.title}"
    body = (
        f"{incident.title}\n\n"
        f"Severity: {incident.severity}\nStatus: {incident.status}\nService: {incident.service}\n"
        f"Impact: {incident.impact}\n\n{web}/incidents/{incident_id}\n"
    )
    await conn.execute(
        text(QUEUE),
        {
            "key": f"incident.{event}:{incident_id}",
            "kind": f"incident.{event}",
            "incident": incident_id,
            "to": [t.group_email for t in teams],
            "cc": [on_call[t.id].email for t in teams if t.id in on_call],
            "subject": f"[InfraWatch] {title}",
            "body": body,
        },
    )
    missing = [t for t in teams if t.id not in on_call]
    if not missing:
        return
    admins = (
        await conn.scalars(
            text(
                "SELECT u.email FROM users u JOIN user_roles r ON r.user_id = u.id "
                "WHERE r.role = 'admin' ORDER BY u.email"
            )
        )
    ).all()
    for team in missing:
        if not admins:
            break
        await conn.execute(
            text(QUEUE),
            {
                "key": f"oncall.missing:{team.id}:{event}:{incident_id}",
                "kind": "oncall.missing",
                "incident": incident_id,
                "to": admins,
                "cc": [],
                "subject": f"[InfraWatch] {team.name} has no on-call for #{incident.number}",
                "body": (
                    f"Nobody is on call for {team.name}, so the email for #{incident.number} "
                    f"went to {team.group_email} only. Set a rotation at {web}/oncall.\n\n{body}"
                ),
            },
        )

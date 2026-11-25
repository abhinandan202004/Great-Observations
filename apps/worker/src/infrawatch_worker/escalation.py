"""Escalation sweep: unacknowledged incidents move along each involved team's on-call rotation."""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_core.escalation import next_escalation
from infrawatch_core.oncall import Rotation
from infrawatch_worker.events import publish

# Every team on an incident that was never acknowledged, with how far it has escalated already.
DUE = (
    "SELECT i.id, i.number, i.title, i.severity, i.raised_at, p.escalate_minutes, "
    "t.id AS team_id, t.name AS team, t.group_email, "
    "(SELECT count(*) FROM escalations e WHERE e.incident_id = i.id AND e.team_id = t.id) AS done "
    "FROM incidents i JOIN sla_policies p ON p.severity = i.severity "
    "JOIN team_tasks tt ON tt.incident_id = i.id JOIN teams t ON t.id = tt.team_id "
    "WHERE p.escalate_minutes IS NOT NULL AND i.status <> 'closed' AND NOT EXISTS "
    "(SELECT 1 FROM status_events s WHERE s.incident_id = i.id AND s.to_status = 'acknowledged')"
)


async def _rotations(conn: AsyncConnection) -> tuple[dict[UUID, Rotation], dict[str, str]]:
    members: dict[UUID, list[str]] = defaultdict(list)
    emails = {}
    for m in await conn.execute(
        text(
            "SELECT m.team_id, u.id, u.email FROM oncall_members m "
            "JOIN users u ON u.id = m.user_id ORDER BY m.team_id, m.position"
        )
    ):
        members[m.team_id].append(str(m.id))
        emails[str(m.id)] = m.email
    rotations = {
        r.team_id: Rotation(members[r.team_id], r.handover_local, r.time_zone, r.shift_days)
        for r in await conn.execute(text("SELECT * FROM oncall_rotations"))
    }
    return rotations, emails


async def sweep(conn: AsyncConnection, now: datetime) -> int:
    """Make every escalation that is due; return how many were made."""
    rotations, emails = await _rotations(conn)
    web = os.environ.get("WEB_URL", "http://localhost:3000")
    made = 0
    for row in (await conn.execute(text(DUE))).all():
        rotation = rotations.get(row.team_id)
        if rotation is None:
            continue
        every = timedelta(minutes=row.escalate_minutes)
        escalation = next_escalation(rotation, row.raised_at, now, every, row.done)
        if escalation is None:
            continue
        inserted = await conn.scalar(
            text(
                "INSERT INTO escalations (incident_id, team_id, step, from_user_id, to_user_id) "
                "VALUES (:incident, :team, :step, :from_user, :to_user) "
                "ON CONFLICT DO NOTHING RETURNING id"
            ),
            {
                "incident": row.id,
                "team": row.team_id,
                "step": escalation.step,
                "from_user": escalation.from_member,
                "to_user": escalation.to_member,
            },
        )
        if inserted is None:
            continue
        title = f"{row.severity} #{row.number} Escalated to you: {row.title}"
        await conn.execute(
            text(
                "INSERT INTO outbox (idempotency_key, kind, incident_id, to_addresses, "
                "cc_addresses, subject, body) VALUES (:key, 'incident.escalated', :incident, "
                "CAST(:to AS text[]), CAST(:cc AS text[]), :subject, :body)"
            ),
            {
                "key": f"incident.escalated:{row.id}:{row.team_id}:{escalation.step}",
                "incident": row.id,
                "to": [emails[escalation.to_member]],
                "cc": [row.group_email],
                "subject": f"[InfraWatch] {title}",
                "body": (
                    f"{row.title} is still unacknowledged, so it now passes to you for "
                    f"{row.team} (escalation {escalation.step}, one every "
                    f"{row.escalate_minutes} minutes).\n\n{web}/incidents/{row.id}\n"
                ),
            },
        )
        await conn.execute(
            text(
                "INSERT INTO audit_log (actor_id, action, target_type, target_id, detail) "
                "VALUES (NULL, 'incident.escalate', 'incident', :incident, CAST(:detail AS jsonb))"
            ),
            {
                "incident": str(row.id),
                "detail": json.dumps(
                    {
                        "team": row.team,
                        "step": str(escalation.step),
                        "from": escalation.from_member,
                        "to": escalation.to_member,
                    }
                ),
            },
        )
        await publish(conn, row.id, "escalation")
        made += 1
    return made

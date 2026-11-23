"""Alert evaluation: every enabled rule against its recent samples, repeats folded into one."""

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_core.alerting import Comparator, Rule, firing_since

STALE = timedelta(seconds=60)  # no sample for this long means the data stopped
CONTEXT = timedelta(minutes=10)  # extra history kept in the snapshot, before the breach


async def evaluate(conn: AsyncConnection, now: datetime) -> int:
    """Evaluate every enabled rule once; return how many drafts were created."""
    created = 0
    rules = await conn.execute(text("SELECT * FROM alert_rules WHERE enabled ORDER BY name"))
    for rule in rules.all():
        duration = timedelta(seconds=rule.duration_seconds)
        samples = [
            (row.time, row.value)
            for row in await conn.execute(
                text(
                    "SELECT time, value FROM metric_samples WHERE service_id = :service "
                    "AND metric = :metric AND time > :since ORDER BY time"
                ),
                {
                    "service": rule.service_id,
                    "metric": rule.metric,
                    "since": now - duration - CONTEXT,
                },
            )
        ]
        check = Rule(Comparator(rule.comparator), rule.threshold, duration)
        start = firing_since(check, samples, now, STALE)
        if start is not None:
            created += await _fire(conn, rule, start, samples)
    return created


async def _fire(
    conn: AsyncConnection, rule: Row[Any], start: datetime, samples: list[tuple[datetime, float]]
) -> int:
    newest = samples[-1][0]
    # The open alert for this rule: a draft, or one raised into an incident that is not closed.
    folded = await conn.execute(
        text(
            "UPDATE alerts a SET last_fired_at = :newest, "
            "fire_count = fire_count + CASE WHEN :start > a.last_fired_at THEN 1 ELSE 0 END "
            "WHERE a.rule_id = :rule AND (a.state = 'draft' OR (a.state = 'raised' AND EXISTS "
            "(SELECT 1 FROM incidents i WHERE i.id = a.incident_id AND i.status <> 'closed'))) "
            "RETURNING a.id"
        ),
        {"rule": rule.id, "start": start, "newest": newest},
    )
    if folded.first() is not None:
        return 0
    snapshot = [{"time": t.isoformat(), "value": v} for t, v in samples]
    inserted = await conn.execute(
        text(
            "INSERT INTO alerts (rule_id, service_id, metric, severity, breach_started_at, "
            "fired_at, last_fired_at, snapshot) VALUES (:rule, :service, :metric, :severity, "
            ":start, :newest, :newest, CAST(:snapshot AS jsonb)) "
            "ON CONFLICT DO NOTHING RETURNING id"
        ),
        {
            "rule": rule.id,
            "service": rule.service_id,
            "metric": rule.metric,
            "severity": rule.severity,
            "start": start,
            "newest": newest,
            "snapshot": json.dumps(snapshot),
        },
    )
    return int(inserted.first() is not None)

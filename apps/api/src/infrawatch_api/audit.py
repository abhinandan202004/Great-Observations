"""Audit writer: one row per mutating call, written in the same transaction as the change."""

import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def record(
    conn: AsyncConnection,
    *,
    actor_id: UUID | None,
    action: str,
    target_type: str,
    target_id: str,
    detail: dict[str, str] | None = None,
) -> None:
    await conn.execute(
        text(
            "INSERT INTO audit_log (actor_id, action, target_type, target_id, detail) "
            "VALUES (:actor_id, :action, :target_type, :target_id, CAST(:detail AS jsonb))"
        ),
        {
            "actor_id": actor_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "detail": json.dumps(detail or {}),
        },
    )

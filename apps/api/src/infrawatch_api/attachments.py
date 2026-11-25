"""Incident attachments: evidence copied at attachment time, so it never changes afterwards."""

import json
import unicodedata
from datetime import datetime, timedelta
from typing import Annotated, Any
from urllib.parse import quote
from uuid import UUID, uuid4

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import AwareDatetime, BaseModel, Field, HttpUrl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api import access, storage
from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import current_user_id
from infrawatch_api.events import publish
from infrawatch_api.incidents import ensure_open, lock_incident
from infrawatch_core.files import MAX_BYTES, sniff
from infrawatch_core.policy import Capability, permits

router = APIRouter(tags=["attachments"])
DETAIL = Depends(require(Capability.VIEW_INCIDENT_DETAIL))
MAX_POINTS = 2000
MAX_SPAN = timedelta(days=7)


class Attachment(BaseModel):
    id: UUID
    kind: str
    title: str
    created_by: str
    created_at: datetime
    data: dict[str, Any]
    file_name: str | None
    content_type: str | None
    size_bytes: int | None


class SnapshotIn(BaseModel):
    service: str
    metric: str
    since: AwareDatetime
    until: AwareDatetime
    title: str | None = Field(default=None, max_length=200)


class LogExcerptIn(BaseModel):
    ids: list[UUID] = Field(min_length=1, max_length=500)
    title: str | None = Field(default=None, max_length=200)


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    url: HttpUrl | None = None  # http or https only; a link if set, a plain note if not
    title: str | None = Field(default=None, max_length=200)


async def _working_on(
    request: Request, conn: AsyncConnection, incident_id: UUID, actor: UUID
) -> None:
    """Lock the open incident; only someone who may update it may attach evidence to it."""
    roles = await access.load_roles(request, actor)
    current, relation = await lock_incident(conn, incident_id, actor)
    if not permits(roles, Capability.UPDATE_STATUS, relation):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not working on this incident")
    ensure_open(current)


async def _add(
    conn: AsyncConnection,
    incident_id: UUID,
    actor: UUID,
    kind: str,
    title: str,
    data: dict[str, Any] | None = None,
    file: dict[str, Any] | None = None,
) -> UUID:
    attachment_id: UUID = (
        await conn.execute(
            text(
                "INSERT INTO attachments (incident_id, kind, title, created_by, data, "
                "object_key, file_name, content_type, size_bytes) VALUES (:incident, :kind, "
                ":title, :actor, CAST(:data AS jsonb), :object_key, :file_name, :content_type, "
                ":size_bytes) RETURNING id"
            ),
            {
                "incident": incident_id,
                "kind": kind,
                "title": title,
                "actor": actor,
                "data": json.dumps(data or {}),
                **(
                    file or dict.fromkeys(("object_key", "file_name", "content_type", "size_bytes"))
                ),
            },
        )
    ).scalar_one()
    await record(
        conn,
        actor_id=actor,
        action="attachment.add",
        target_type="incident",
        target_id=str(incident_id),
        detail={"attachment": str(attachment_id), "kind": kind, "title": title},
    )
    await publish(conn, incident_id, "attachment")
    return attachment_id


@router.get("/incidents/{incident_id}/attachments", dependencies=[DETAIL])
async def list_attachments(incident_id: UUID, request: Request) -> list[Attachment]:
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(
            text(
                "SELECT a.id, a.kind, a.title, u.display_name AS created_by, a.created_at, a.data, "
                "a.file_name, a.content_type, a.size_bytes FROM attachments a "
                "JOIN users u ON u.id = a.created_by WHERE a.incident_id = :id "
                "ORDER BY a.created_at"
            ),
            {"id": incident_id},
        )
        return [Attachment.model_validate(r, from_attributes=True) for r in rows]


@router.post("/incidents/{incident_id}/attachments/snapshot", status_code=status.HTTP_201_CREATED)
async def attach_snapshot(
    incident_id: UUID,
    body: SnapshotIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> dict[str, str]:
    if not timedelta(0) < body.until - body.since <= MAX_SPAN:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "The range must be positive and at most 7 days"
        )
    async with request.app.state.engine.begin() as conn:
        await _working_on(request, conn, incident_id, actor)
        points = (
            await conn.execute(
                text(
                    "SELECT m.time, m.value FROM metric_samples m "
                    "JOIN services s ON s.id = m.service_id WHERE s.name = :service "
                    "AND m.metric = :metric AND m.time BETWEEN :since AND :until "
                    "ORDER BY m.time LIMIT :limit"
                ),
                {**body.model_dump(exclude={"title"}), "limit": MAX_POINTS + 1},
            )
        ).all()
        if not points:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "No samples in that range")
        if len(points) > MAX_POINTS:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Too many samples; narrow the range"
            )
        data = {
            "service": body.service,
            "metric": body.metric,
            "since": body.since.isoformat(),
            "until": body.until.isoformat(),
            "points": [{"time": p.time.isoformat(), "value": p.value} for p in points],
        }
        title = body.title or f"{body.metric} on {body.service}"
        attachment = await _add(conn, incident_id, actor, "metric_snapshot", title, data)
    return {"id": str(attachment)}


@router.post("/incidents/{incident_id}/attachments/logs", status_code=status.HTTP_201_CREATED)
async def attach_logs(
    incident_id: UUID,
    body: LogExcerptIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        await _working_on(request, conn, incident_id, actor)
        lines = (
            await conn.execute(
                text(
                    "SELECT l.time, s.name AS service, l.level, l.message, l.correlation_id "
                    "FROM log_entries l JOIN services s ON s.id = l.service_id "
                    "WHERE l.id = ANY(CAST(:ids AS uuid[])) ORDER BY l.time"
                ),
                {"ids": list(set(body.ids))},
            )
        ).all()
        if len(lines) != len(set(body.ids)):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Some log lines were not found"
            )
        data = {"lines": [{**line._mapping, "time": line.time.isoformat()} for line in lines]}
        title = body.title or f"{len(lines)} log line{'s' * (len(lines) != 1)}"
        attachment = await _add(conn, incident_id, actor, "log_excerpt", title, data)
    return {"id": str(attachment)}


@router.post("/incidents/{incident_id}/attachments/note", status_code=status.HTTP_201_CREATED)
async def attach_note(
    incident_id: UUID,
    body: NoteIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        await _working_on(request, conn, incident_id, actor)
        kind = "link" if body.url else "note"
        data = {"text": body.text, "url": str(body.url) if body.url else None}
        title = body.title or (str(body.url) if body.url else body.text[:80])
        attachment = await _add(conn, incident_id, actor, kind, title, data)
    return {"id": str(attachment)}


@router.post("/incidents/{incident_id}/attachments/file", status_code=status.HTTP_201_CREATED)
async def attach_file(
    incident_id: UUID,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
    name: Annotated[str, Query(min_length=1, max_length=200)],
) -> dict[str, str]:
    """The file is the raw request body; ``name`` is its original file name."""
    file_name = _safe_name(name)
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Files may be at most 10 MB")
    async with request.app.state.engine.begin() as conn:
        # Refuse before reading the body, so nobody without access can push 10 MB at us.
        await _working_on(request, conn, incident_id, actor)
        data = bytearray()
        async for chunk in request.stream():
            data += chunk
            if len(data) > MAX_BYTES:
                raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Files may be at most 10 MB")
        content_type = sniff(file_name, bytes(data))
        if content_type is None:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Only PNG, JPEG, GIF, WebP, PDF and .txt or .log text files are allowed",
            )
        key = f"{incident_id}/{uuid4()}"
        try:
            await storage.put(key, bytes(data), content_type)
        except (BotoCoreError, ClientError):
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Attachment storage is unavailable"
            ) from None
        # shortcut: an object stored just before a failed commit is left behind unreferenced;
        # add a sweep for keys with no attachment row if storage use ever matters.
        attachment = await _add(
            conn,
            incident_id,
            actor,
            "file",
            file_name,
            file={
                "object_key": key,
                "file_name": file_name,
                "content_type": content_type,
                "size_bytes": len(data),
            },
        )
    return {"id": str(attachment)}


@router.get("/attachments/{attachment_id}/file", dependencies=[DETAIL])
async def download_file(attachment_id: UUID, request: Request) -> Response:
    async with request.app.state.engine.connect() as conn:
        row = (
            await conn.execute(
                text(
                    "SELECT object_key, file_name, content_type FROM attachments "
                    "WHERE id = :id AND kind = 'file'"
                ),
                {"id": attachment_id},
            )
        ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such file")
    try:
        content = await storage.get(row.object_key)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Attachment storage is unavailable"
        ) from None
    # Uploaded bytes are never rendered as part of the app: always a download, typed as sniffed,
    # and locked down even if someone opens the URL directly.
    return Response(
        content,
        media_type=row.content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(row.file_name)}",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; sandbox",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cache-Control": "private, no-store",
        },
    )


def _safe_name(name: str) -> str:
    """The base name only, without control characters, so it is safe in a header and a page."""
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = "".join(c for c in base if unicodedata.category(c)[0] != "C").strip()
    return cleaned or "file"

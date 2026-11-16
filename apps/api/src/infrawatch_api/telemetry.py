"""Telemetry ingest and query endpoints."""

import hashlib
import hmac
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import AwareDatetime, BaseModel, Field, ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

router = APIRouter(tags=["telemetry"])

MAX_QUERY_POINTS = 2000


class MetricSample(BaseModel):
    time: AwareDatetime
    metric: str = Field(min_length=1, max_length=100)
    value: float = Field(allow_inf_nan=False)


class MetricBatch(BaseModel):
    service: str
    samples: list[MetricSample] = Field(min_length=1, max_length=1000)


class LogEntry(BaseModel):
    id: UUID
    time: AwareDatetime
    level: Literal["debug", "info", "warning", "error"]
    message: str = Field(min_length=1, max_length=2000)
    correlation_id: str | None = Field(default=None, max_length=100)


class LogBatch(BaseModel):
    service: str
    entries: list[LogEntry] = Field(min_length=1, max_length=1000)


class ChangeEvent(BaseModel):
    id: UUID
    time: AwareDatetime
    service: str
    kind: Literal["deploy", "config", "feature_flag"]
    summary: str = Field(min_length=1, max_length=500)


class IngestResult(BaseModel):
    accepted: int


class MetricPoint(BaseModel):
    time: AwareDatetime
    value: float


bearer = HTTPBearer(auto_error=False)


def require_ingest_key(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> None:
    # shortcut: any valid key may write for any service;
    # bind keys to services when M3 adds key management.
    keys: tuple[str, ...] = request.app.state.ingest_keys
    token = credentials.credentials if credentials else ""
    if not any(hmac.compare_digest(token.encode(), key.encode()) for key in keys):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Missing or invalid ingest API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def service_id(conn: AsyncConnection, name: str) -> object:
    found = await conn.scalar(text("SELECT id FROM services WHERE name = :name"), {"name": name})
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown service: {name}")
    return found


@router.post("/ingest/metrics", dependencies=[Depends(require_ingest_key)])
async def ingest_metrics(batch: MetricBatch, request: Request) -> IngestResult:
    engine: AsyncEngine = request.app.state.engine
    async with engine.begin() as conn:
        sid = await service_id(conn, batch.service)
        await conn.execute(
            text(
                "INSERT INTO metric_samples (time, service_id, metric, value) "
                "VALUES (:time, :service_id, :metric, :value) ON CONFLICT DO NOTHING"
            ),
            [{"service_id": sid, **s.model_dump()} for s in batch.samples],
        )
    return IngestResult(accepted=len(batch.samples))


@router.post("/ingest/logs", dependencies=[Depends(require_ingest_key)])
async def ingest_logs(batch: LogBatch, request: Request) -> IngestResult:
    engine: AsyncEngine = request.app.state.engine
    async with engine.begin() as conn:
        sid = await service_id(conn, batch.service)
        await conn.execute(
            text(
                "INSERT INTO log_entries (id, time, service_id, level, message, correlation_id) "
                "VALUES (:id, :time, :service_id, :level, :message, :correlation_id) "
                "ON CONFLICT DO NOTHING"
            ),
            [{"service_id": sid, **e.model_dump()} for e in batch.entries],
        )
    return IngestResult(accepted=len(batch.entries))


@router.post("/ingest/changes")
async def ingest_change(request: Request) -> IngestResult:
    """Change-event webhook for CI/CD and configuration systems.

    The sender signs the exact request body with HMAC-SHA256 and the shared secret, and
    sends ``X-Signature-256: sha256=<hex digest>``. The signature is checked before the
    body is parsed. A replayed request is harmless: the event id is the primary key.
    """
    secret: str = request.app.state.change_webhook_secret
    body = await request.body()
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    given = request.headers.get("X-Signature-256", "")
    if not secret or not hmac.compare_digest(given.encode(), expected.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid signature.")
    try:
        event = ChangeEvent.model_validate_json(body)
    except ValidationError as error:
        raise HTTPException(422, str(error)) from error

    engine: AsyncEngine = request.app.state.engine
    async with engine.begin() as conn:
        sid = await service_id(conn, event.service)
        await conn.execute(
            text(
                "INSERT INTO change_events (id, time, service_id, kind, summary) "
                "VALUES (:id, :time, :service_id, :kind, :summary) ON CONFLICT DO NOTHING"
            ),
            {"service_id": sid, **event.model_dump(exclude={"service"})},
        )
    return IngestResult(accepted=1)


# Unauthenticated until M3 puts every read endpoint behind login (phase-1-plan, M2 decisions).
@router.get("/services/{service}/metrics/{metric}")
async def metric_series(
    service: str, metric: str, since: AwareDatetime, request: Request
) -> list[MetricPoint]:
    """Samples since ``since``, oldest first.

    shortcut: returns at most the newest 2000 raw points with no downsampling;
    add time_bucket aggregation when the chart shows ranges longer than a few hours.
    """
    engine: AsyncEngine = request.app.state.engine
    async with engine.connect() as conn:
        sid = await service_id(conn, service)
        rows = await conn.execute(
            text(
                "SELECT time, value FROM ("
                "  SELECT time, value FROM metric_samples"
                "  WHERE service_id = :sid AND metric = :metric AND time >= :since"
                "  ORDER BY time DESC LIMIT :limit"
                ") newest ORDER BY time"
            ),
            {"sid": sid, "metric": metric, "since": since, "limit": MAX_QUERY_POINTS},
        )
        return [MetricPoint(time=row.time, value=row.value) for row in rows]

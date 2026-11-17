"""Incidents: raise, read, move through the lifecycle, change severity."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api import access
from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import current_user_id
from infrawatch_core.lifecycle import (
    NEEDS_REASON,
    Move,
    Severity,
    Status,
    TransitionError,
    classify,
)
from infrawatch_core.policy import Capability, Relation, allows, permits

router = APIRouter(tags=["incidents"])

SUMMARY = (
    "SELECT i.id, i.number, i.title, i.impact, i.severity, i.status, i.raised_at, "
    "s.name AS service FROM incidents i JOIN services s ON s.id = i.service_id"
)


class RaiseIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    impact: str = Field(min_length=1, max_length=2000)
    description: str = Field(min_length=1, max_length=10000)
    severity: Severity
    service: str


class StatusIn(BaseModel):
    status: Status
    reason: str | None = Field(default=None, max_length=2000)


class SeverityIn(BaseModel):
    severity: Severity


class Summary(BaseModel):
    """What every role that may see incidents sees: status and impact only."""

    id: UUID
    number: int
    title: str
    impact: str
    severity: Severity
    status: Status
    service: str
    raised_at: datetime


class StatusEvent(BaseModel):
    id: int
    time: datetime
    actor: str
    from_status: Status | None
    to_status: Status
    reason: str | None
    reopens: int | None


class TeamTask(BaseModel):
    team: str
    assignee: str | None


class Detail(Summary):
    description: str
    caller: str
    teams: list[TeamTask]
    timeline: list[StatusEvent]


async def _summary(conn: AsyncConnection, incident_id: UUID) -> Summary:
    row = (await conn.execute(text(f"{SUMMARY} WHERE i.id = :id"), {"id": incident_id})).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such incident")
    return Summary.model_validate(row, from_attributes=True)


async def _detail(conn: AsyncConnection, incident_id: UUID) -> Detail:
    summary = await _summary(conn, incident_id)
    extra = (
        await conn.execute(
            text(
                "SELECT i.description, u.display_name AS caller FROM incidents i "
                "JOIN users u ON u.id = i.caller_id WHERE i.id = :id"
            ),
            {"id": incident_id},
        )
    ).one()
    teams = await conn.execute(
        text(
            "SELECT t.name AS team, u.display_name AS assignee FROM team_tasks tt "
            "JOIN teams t ON t.id = tt.team_id LEFT JOIN users u ON u.id = tt.assignee_id "
            "WHERE tt.incident_id = :id ORDER BY t.name"
        ),
        {"id": incident_id},
    )
    timeline = await conn.execute(
        text(
            "SELECT e.id, e.time, u.display_name AS actor, e.from_status, e.to_status, e.reason, "
            "e.reopens FROM status_events e JOIN users u ON u.id = e.actor_id "
            "WHERE e.incident_id = :id ORDER BY e.id"
        ),
        {"id": incident_id},
    )
    return Detail(
        **summary.model_dump(),
        description=extra.description,
        caller=extra.caller,
        teams=[TeamTask.model_validate(r, from_attributes=True) for r in teams],
        timeline=[StatusEvent.model_validate(r, from_attributes=True) for r in timeline],
    )


@router.post("/incidents", status_code=status.HTTP_201_CREATED)
async def raise_incident(
    body: RaiseIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.RAISE_INCIDENT))],
) -> Detail:
    async with request.app.state.engine.begin() as conn:
        service = (
            await conn.execute(
                text("SELECT id, team_id FROM services WHERE name = :name"), {"name": body.service}
            )
        ).first()
        if service is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown service")
        incident_id: UUID = (
            await conn.execute(
                text(
                    "INSERT INTO incidents "
                    "(title, impact, description, severity, service_id, caller_id) "
                    "VALUES (:title, :impact, :description, :severity, :service_id, :actor) "
                    "RETURNING id"
                ),
                {
                    **body.model_dump(exclude={"service"}),
                    "service_id": service.id,
                    "actor": actor,
                },
            )
        ).scalar_one()
        await conn.execute(
            text(
                "INSERT INTO status_events (incident_id, actor_id, to_status) "
                "VALUES (:id, :actor, 'raised')"
            ),
            {"id": incident_id, "actor": actor},
        )
        # The owning team of the service starts with a task; more teams join in a later step.
        await conn.execute(
            text("INSERT INTO team_tasks (incident_id, team_id) VALUES (:id, :team)"),
            {"id": incident_id, "team": service.team_id},
        )
        await record(
            conn,
            actor_id=actor,
            action="incident.raise",
            target_type="incident",
            target_id=str(incident_id),
            detail={"severity": body.severity.value, "service": body.service},
        )
        return await _detail(conn, incident_id)


@router.get("/incidents", dependencies=[Depends(require(Capability.VIEW_INCIDENT_STATUS))])
async def list_incidents(request: Request) -> list[Summary]:
    # shortcut: the newest 200 with no paging or filter; enough at demo scale.
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(text(f"{SUMMARY} ORDER BY i.number DESC LIMIT 200"))
        return [Summary.model_validate(r, from_attributes=True) for r in rows]


@router.get("/incidents/{incident_id}")
async def get_incident(
    incident_id: UUID,
    request: Request,
    user: Annotated[UUID, Depends(require(Capability.VIEW_INCIDENT_STATUS))],
) -> Detail | Summary:
    roles = await access.load_roles(request, user)
    async with request.app.state.engine.connect() as conn:
        if allows(roles, Capability.VIEW_INCIDENT_DETAIL):
            return await _detail(conn, incident_id)
        return await _summary(conn, incident_id)


@router.post("/incidents/{incident_id}/status")
async def change_status(
    incident_id: UUID,
    body: StatusIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> Detail:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        row = (
            await conn.execute(
                text(
                    "SELECT i.status, i.caller_id = :me AS caller, "
                    "EXISTS (SELECT 1 FROM team_tasks tt JOIN memberships m "
                    "ON m.team_id = tt.team_id WHERE tt.incident_id = i.id AND m.user_id = :me) "
                    "AS team_member, "
                    "EXISTS (SELECT 1 FROM team_tasks tt JOIN memberships m "
                    "ON m.team_id = tt.team_id WHERE tt.incident_id = i.id AND m.user_id = :me "
                    "AND m.is_lead) AS lead "
                    "FROM incidents i WHERE i.id = :id FOR UPDATE OF i"
                ),
                {"id": incident_id, "me": actor},
            )
        ).first()
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such incident")
        relation = Relation(caller=row.caller, team_member=row.team_member, lead=row.lead)
        may_update = permits(roles, Capability.UPDATE_STATUS, relation)
        if not (may_update or relation.caller):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not working on this incident")
        current = Status(row.status)
        try:
            move = classify(current, body.status)
        except TransitionError as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None
        if move in (Move.REOPEN, Move.CLOSE):
            if not permits(roles, Capability.CLOSE_INCIDENT, relation):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the caller may do this")
        elif not may_update:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not working on this incident")
        reason = (body.reason or "").strip() or None
        if move in NEEDS_REASON and reason is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "A reason is required")
        if move is Move.CLOSE:
            # shortcut: runbooks arrive in M7; until then no incident has an approved one.
            raise HTTPException(status.HTTP_409_CONFLICT, "Closing needs an approved runbook")
        reopens = None
        if move is Move.REOPEN:
            reopens = await conn.scalar(
                text(
                    "SELECT max(id) FROM status_events "
                    "WHERE incident_id = :id AND to_status = 'resolved'"
                ),
                {"id": incident_id},
            )
        await conn.execute(
            text("UPDATE incidents SET status = :status WHERE id = :id"),
            {"status": body.status.value, "id": incident_id},
        )
        await conn.execute(
            text(
                "INSERT INTO status_events "
                "(incident_id, actor_id, from_status, to_status, reason, reopens) "
                "VALUES (:id, :actor, :from_status, :to_status, :reason, :reopens)"
            ),
            {
                "id": incident_id,
                "actor": actor,
                "from_status": current.value,
                "to_status": body.status.value,
                "reason": reason,
                "reopens": reopens,
            },
        )
        await record(
            conn,
            actor_id=actor,
            action=f"incident.{move.value}",
            target_type="incident",
            target_id=str(incident_id),
            detail={"from": current.value, "to": body.status.value, "reason": reason or ""},
        )
        return await _detail(conn, incident_id)


@router.post("/incidents/{incident_id}/severity")
async def change_severity(
    incident_id: UUID,
    body: SeverityIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.CHANGE_SEVERITY))],
) -> Detail:
    async with request.app.state.engine.begin() as conn:
        row = (
            await conn.execute(
                text("SELECT severity, status FROM incidents WHERE id = :id FOR UPDATE"),
                {"id": incident_id},
            )
        ).first()
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such incident")
        if row.status == Status.CLOSED:
            raise HTTPException(status.HTTP_409_CONFLICT, "A closed incident cannot change")
        await conn.execute(
            text("UPDATE incidents SET severity = :severity WHERE id = :id"),
            {"severity": body.severity.value, "id": incident_id},
        )
        await record(
            conn,
            actor_id=actor,
            action="incident.severity",
            target_type="incident",
            target_id=str(incident_id),
            detail={"from": row.severity, "to": body.severity.value},
        )
        return await _detail(conn, incident_id)

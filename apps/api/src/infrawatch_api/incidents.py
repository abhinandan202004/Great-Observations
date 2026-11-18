"""Incidents: raise, read, move through the lifecycle, team tasks, severity and SLA policy."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api import access
from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import current_user_id
from infrawatch_core import sla
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
MAX_MINUTES = 366 * 24 * 60


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


class TeamIn(BaseModel):
    team_id: UUID


class AssigneeIn(BaseModel):
    user_id: UUID


class ChecklistItemIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class CheckIn(BaseModel):
    done: bool


class SlaPolicy(BaseModel):
    severity: Severity
    acknowledge_minutes: int = Field(ge=1, le=MAX_MINUTES)
    resolve_minutes: int = Field(ge=1, le=MAX_MINUTES)


class SlaPolicyIn(BaseModel):
    acknowledge_minutes: int = Field(ge=1, le=MAX_MINUTES)
    resolve_minutes: int = Field(ge=1, le=MAX_MINUTES)


class SlaTimer(BaseModel):
    due: datetime
    stopped_at: datetime | None
    remaining_seconds: int
    breached: bool


class Summary(BaseModel):
    """What every role that may see incidents sees: status, impact and SLA only."""

    id: UUID
    number: int
    title: str
    impact: str
    severity: Severity
    status: Status
    service: str
    raised_at: datetime
    acknowledge: SlaTimer
    resolve: SlaTimer


class StatusEvent(BaseModel):
    id: int
    time: datetime
    actor: str
    from_status: Status | None
    to_status: Status
    reason: str | None
    reopens: int | None


class ChecklistItem(BaseModel):
    id: UUID
    text: str
    done: bool


class TeamTask(BaseModel):
    team_id: UUID
    team: str
    assignee_id: UUID | None
    assignee: str | None
    checklist: list[ChecklistItem]


class Detail(Summary):
    description: str
    caller: str
    teams: list[TeamTask]
    timeline: list[StatusEvent]


class Member(BaseModel):
    id: UUID
    display_name: str
    is_lead: bool


class Team(BaseModel):
    id: UUID
    name: str
    members: list[Member]


def _timer(timer: sla.Timer) -> SlaTimer:
    return SlaTimer(
        due=timer.due,
        stopped_at=timer.stopped_at,
        remaining_seconds=int(timer.remaining.total_seconds()),
        breached=timer.breached,
    )


async def _summaries(conn: AsyncConnection, tail: str, params: dict[str, Any]) -> list[Summary]:
    rows = (await conn.execute(text(f"{SUMMARY} {tail}"), params)).all()
    if not rows:
        return []
    policies = {
        p.severity: sla.Policy(
            acknowledge=timedelta(minutes=p.acknowledge_minutes),
            resolve=timedelta(minutes=p.resolve_minutes),
        )
        for p in await conn.execute(text("SELECT * FROM sla_policies"))
    }
    events: dict[UUID, list[tuple[datetime, Status]]] = defaultdict(list)
    for e in await conn.execute(
        text(
            "SELECT incident_id, time, to_status FROM status_events "
            "WHERE incident_id = ANY(CAST(:ids AS uuid[])) ORDER BY id"
        ),
        {"ids": [r.id for r in rows]},
    ):
        events[e.incident_id].append((e.time, Status(e.to_status)))
    now = datetime.now(UTC)
    summaries = []
    for r in rows:
        ack, resolve = sla.timers(events[r.id], policies[r.severity], now)
        summaries.append(Summary(**r._mapping, acknowledge=_timer(ack), resolve=_timer(resolve)))
    return summaries


async def _summary(conn: AsyncConnection, incident_id: UUID) -> Summary:
    found = await _summaries(conn, "WHERE i.id = :id", {"id": incident_id})
    if not found:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such incident")
    return found[0]


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
    checklists: dict[UUID, list[ChecklistItem]] = defaultdict(list)
    for item in await conn.execute(
        text(
            "SELECT ci.id, ci.text, ci.done, tt.team_id FROM checklist_items ci "
            "JOIN team_tasks tt ON tt.id = ci.task_id WHERE tt.incident_id = :id "
            "ORDER BY ci.created_at, ci.id"
        ),
        {"id": incident_id},
    ):
        checklists[item.team_id].append(ChecklistItem.model_validate(item, from_attributes=True))
    teams = await conn.execute(
        text(
            "SELECT tt.team_id, t.name AS team, tt.assignee_id, u.display_name AS assignee "
            "FROM team_tasks tt JOIN teams t ON t.id = tt.team_id "
            "LEFT JOIN users u ON u.id = tt.assignee_id WHERE tt.incident_id = :id ORDER BY t.name"
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
        teams=[TeamTask(**t._mapping, checklist=checklists[t.team_id]) for t in teams],
        timeline=[StatusEvent.model_validate(r, from_attributes=True) for r in timeline],
    )


async def _lock(
    conn: AsyncConnection, incident_id: UUID, actor: UUID, team_id: UUID | None = None
) -> tuple[Status, Relation]:
    """Lock the incident and say how the actor relates to it, or to one team's task on it."""
    # bool_or over the actor's memberships: NULL is not on the team(s), false a member, true a lead.
    row = (
        await conn.execute(
            text(
                "SELECT i.status, i.caller_id = :me AS caller, "
                "(SELECT bool_or(m.is_lead) FROM team_tasks tt "
                "JOIN memberships m ON m.team_id = tt.team_id "
                "WHERE tt.incident_id = i.id AND m.user_id = :me "
                "AND (CAST(:team AS uuid) IS NULL OR tt.team_id = CAST(:team AS uuid))) AS lead "
                "FROM incidents i WHERE i.id = :id FOR UPDATE OF i"
            ),
            {"id": incident_id, "me": actor, "team": team_id},
        )
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such incident")
    return Status(row.status), Relation(
        caller=row.caller, team_member=row.lead is not None, lead=bool(row.lead)
    )


def _open(current: Status) -> None:
    if current is Status.CLOSED:
        raise HTTPException(status.HTTP_409_CONFLICT, "A closed incident cannot change")


async def _task_id(conn: AsyncConnection, incident_id: UUID, team_id: UUID) -> UUID:
    task: UUID | None = await conn.scalar(
        text("SELECT id FROM team_tasks WHERE incident_id = :id AND team_id = :team"),
        {"id": incident_id, "team": team_id},
    )
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This team has no task on the incident")
    return task


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
        # The service's owning team starts with a task; other teams join through /teams.
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
        return await _summaries(conn, "ORDER BY i.number DESC LIMIT 200", {})


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
        current, relation = await _lock(conn, incident_id, actor)
        may_update = permits(roles, Capability.UPDATE_STATUS, relation)
        if not (may_update or relation.caller):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not working on this incident")
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
        _open(Status(row.status))
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


@router.post("/incidents/{incident_id}/teams", status_code=status.HTTP_201_CREATED)
async def add_team(
    incident_id: UUID,
    body: TeamIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> Detail:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        current, relation = await _lock(conn, incident_id, actor)
        if not permits(roles, Capability.UPDATE_STATUS, relation):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not working on this incident")
        _open(current)
        team = await conn.scalar(
            text("SELECT name FROM teams WHERE id = :team"), {"team": body.team_id}
        )
        if team is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown team")
        added = await conn.scalar(
            text(
                "INSERT INTO team_tasks (incident_id, team_id) VALUES (:id, :team) "
                "ON CONFLICT DO NOTHING RETURNING id"
            ),
            {"id": incident_id, "team": body.team_id},
        )
        if added is None:
            raise HTTPException(status.HTTP_409_CONFLICT, "This team is already on the incident")
        await record(
            conn,
            actor_id=actor,
            action="incident.team_add",
            target_type="incident",
            target_id=str(incident_id),
            detail={"team": team},
        )
        return await _detail(conn, incident_id)


@router.post("/incidents/{incident_id}/teams/{team_id}/assignee")
async def assign(
    incident_id: UUID,
    team_id: UUID,
    body: AssigneeIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> Detail:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        current, relation = await _lock(conn, incident_id, actor, team_id)
        if not permits(roles, Capability.ASSIGN, relation):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only this team's lead may assign")
        _open(current)
        task = await _task_id(conn, incident_id, team_id)
        member = await conn.scalar(
            text("SELECT 1 FROM memberships WHERE user_id = :user AND team_id = :team"),
            {"user": body.user_id, "team": team_id},
        )
        if member is None:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "The assignee is not on this team"
            )
        before = await conn.scalar(
            text("SELECT assignee_id FROM team_tasks WHERE id = :task"), {"task": task}
        )
        await conn.execute(
            text("UPDATE team_tasks SET assignee_id = :user WHERE id = :task"),
            {"user": body.user_id, "task": task},
        )
        await record(
            conn,
            actor_id=actor,
            action="incident.assign",
            target_type="team_task",
            target_id=str(task),
            detail={"from": str(before or ""), "to": str(body.user_id)},
        )
        return await _detail(conn, incident_id)


@router.post(
    "/incidents/{incident_id}/teams/{team_id}/checklist", status_code=status.HTTP_201_CREATED
)
async def add_checklist_item(
    incident_id: UUID,
    team_id: UUID,
    body: ChecklistItemIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> Detail:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        current, relation = await _lock(conn, incident_id, actor, team_id)
        if not permits(roles, Capability.UPDATE_STATUS, relation):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not on this team")
        _open(current)
        task = await _task_id(conn, incident_id, team_id)
        item = await conn.scalar(
            text("INSERT INTO checklist_items (task_id, text) VALUES (:task, :text) RETURNING id"),
            {"task": task, "text": body.text},
        )
        await record(
            conn,
            actor_id=actor,
            action="checklist.add",
            target_type="checklist_item",
            target_id=str(item),
            detail={"text": body.text},
        )
        return await _detail(conn, incident_id)


@router.post("/incidents/{incident_id}/checklist/{item_id}")
async def check_item(
    incident_id: UUID,
    item_id: UUID,
    body: CheckIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> Detail:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        team_id: UUID | None = await conn.scalar(
            text(
                "SELECT tt.team_id FROM checklist_items ci "
                "JOIN team_tasks tt ON tt.id = ci.task_id "
                "WHERE ci.id = :item AND tt.incident_id = :id"
            ),
            {"item": item_id, "id": incident_id},
        )
        if team_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such checklist item")
        current, relation = await _lock(conn, incident_id, actor, team_id)
        if not permits(roles, Capability.UPDATE_STATUS, relation):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not on this team")
        _open(current)
        await conn.execute(
            text("UPDATE checklist_items SET done = :done WHERE id = :item"),
            {"done": body.done, "item": item_id},
        )
        await record(
            conn,
            actor_id=actor,
            action="checklist.check",
            target_type="checklist_item",
            target_id=str(item_id),
            detail={"done": str(body.done).lower()},
        )
        return await _detail(conn, incident_id)


@router.get("/teams", dependencies=[Depends(require(Capability.VIEW_INCIDENT_DETAIL))])
async def list_teams(request: Request) -> list[Team]:
    async with request.app.state.engine.connect() as conn:
        members: dict[UUID, list[Member]] = defaultdict(list)
        for m in await conn.execute(
            text(
                "SELECT m.team_id, u.id, u.display_name, m.is_lead FROM memberships m "
                "JOIN users u ON u.id = m.user_id ORDER BY u.display_name"
            )
        ):
            members[m.team_id].append(Member.model_validate(m, from_attributes=True))
        teams = await conn.execute(text("SELECT id, name FROM teams ORDER BY name"))
        return [Team(id=t.id, name=t.name, members=members[t.id]) for t in teams]


@router.get("/sla-policies", dependencies=[Depends(require(Capability.VIEW_INCIDENT_STATUS))])
async def list_sla_policies(request: Request) -> list[SlaPolicy]:
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(text("SELECT * FROM sla_policies ORDER BY severity"))
        return [SlaPolicy.model_validate(r, from_attributes=True) for r in rows]


@router.put("/sla-policies/{severity}")
async def set_sla_policy(
    severity: Severity,
    body: SlaPolicyIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
) -> SlaPolicy:
    async with request.app.state.engine.begin() as conn:
        before = (
            await conn.execute(
                text("SELECT * FROM sla_policies WHERE severity = :severity FOR UPDATE"),
                {"severity": severity.value},
            )
        ).one()
        await conn.execute(
            text(
                "UPDATE sla_policies SET acknowledge_minutes = :acknowledge_minutes, "
                "resolve_minutes = :resolve_minutes WHERE severity = :severity"
            ),
            {**body.model_dump(), "severity": severity.value},
        )
        await record(
            conn,
            actor_id=actor,
            action="sla_policy.update",
            target_type="sla_policy",
            target_id=severity.value,
            detail={
                "from": f"{before.acknowledge_minutes}/{before.resolve_minutes}",
                "to": f"{body.acknowledge_minutes}/{body.resolve_minutes}",
            },
        )
    return SlaPolicy(severity=severity, **body.model_dump())

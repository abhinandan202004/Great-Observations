"""On-call rotations: who is on call for each team now, and editing a team's rotation."""

from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, NaiveDatetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api import access
from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import current_user_id
from infrawatch_core.oncall import Rotation, current_shift
from infrawatch_core.policy import Capability, Relation, permits

router = APIRouter(tags=["on-call"])


class Person(BaseModel):
    id: UUID
    display_name: str
    email: str


class RotationOut(BaseModel):
    members: list[Person]
    handover_local: datetime
    time_zone: str
    shift_days: int


class TeamOnCall(BaseModel):
    team_id: UUID
    team: str
    group_email: str
    rotation: RotationOut | None
    on_call: Person | None
    shift_ends_at: datetime | None


class RotationIn(BaseModel):
    members: list[UUID] = Field(min_length=1, max_length=50)
    handover_local: NaiveDatetime  # wall-clock time in time_zone
    time_zone: str = Field(min_length=1, max_length=64)
    shift_days: int = Field(ge=1, le=28)


async def rotations(
    conn: AsyncConnection, team_ids: Sequence[UUID] | None = None
) -> dict[UUID, tuple[RotationOut, Rotation]]:
    """Each team's rotation, as shown and as the core module computes with it."""
    members: dict[UUID, list[Person]] = defaultdict(list)
    for m in await conn.execute(
        text(
            "SELECT m.team_id, u.id, u.display_name, u.email FROM oncall_members m "
            "JOIN users u ON u.id = m.user_id ORDER BY m.team_id, m.position"
        )
    ):
        members[m.team_id].append(Person(id=m.id, display_name=m.display_name, email=m.email))
    found = {}
    for r in await conn.execute(text("SELECT * FROM oncall_rotations")):
        if team_ids is not None and r.team_id not in team_ids:
            continue
        shown = RotationOut(
            members=members[r.team_id],
            handover_local=r.handover_local,
            time_zone=r.time_zone,
            shift_days=r.shift_days,
        )
        people = [str(p.id) for p in shown.members]
        found[r.team_id] = (shown, Rotation(people, r.handover_local, r.time_zone, r.shift_days))
    return found


async def on_call_now(
    conn: AsyncConnection, team_ids: Sequence[UUID], now: datetime
) -> dict[UUID, Person]:
    """Whoever is on call now for each of the teams; a team with nobody on call is left out."""
    found = {}
    for team_id, (shown, rotation) in (await rotations(conn, team_ids)).items():
        shift = current_shift(rotation, now)
        if shift is not None:
            found[team_id] = shown.members[shift.index]
    return found


@router.get("/oncall", dependencies=[Depends(require(Capability.VIEW_INCIDENT_DETAIL))])
async def list_on_call(request: Request) -> list[TeamOnCall]:
    now = datetime.now(UTC)
    async with request.app.state.engine.connect() as conn:
        found = await rotations(conn)
        teams = await conn.execute(text("SELECT id, name, group_email FROM teams ORDER BY name"))
        result = []
        for team in teams:
            shown, rotation = found.get(team.id, (None, None))
            shift = current_shift(rotation, now) if rotation else None
            result.append(
                TeamOnCall(
                    team_id=team.id,
                    team=team.name,
                    group_email=team.group_email,
                    rotation=shown,
                    on_call=shown.members[shift.index] if shown and shift else None,
                    shift_ends_at=shift.ends_at if shift else None,
                )
            )
        return result


@router.put("/teams/{team_id}/oncall")
async def set_rotation(
    team_id: UUID,
    body: RotationIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> TeamOnCall:
    roles = await access.load_roles(request, actor)
    try:
        ZoneInfo(body.time_zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown time zone") from None
    if len(set(body.members)) != len(body.members):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "A person appears twice")
    async with request.app.state.engine.begin() as conn:
        team = (
            await conn.execute(
                text("SELECT name FROM teams WHERE id = :team FOR UPDATE"), {"team": team_id}
            )
        ).first()
        if team is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such team")
        on_team = await conn.scalar(
            text("SELECT 1 FROM memberships WHERE team_id = :team AND user_id = :me"),
            {"team": team_id, "me": actor},
        )
        if not permits(roles, Capability.MANAGE_ONCALL, Relation(team_member=on_team is not None)):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You may not set this team's on-call")
        outsiders = await conn.scalar(
            text(
                "SELECT count(*) FROM unnest(CAST(:members AS uuid[])) AS m(id) WHERE NOT EXISTS "
                "(SELECT 1 FROM memberships WHERE team_id = :team AND user_id = m.id)"
            ),
            {"members": body.members, "team": team_id},
        )
        if outsiders:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Everyone on call must be on this team"
            )
        before = (await rotations(conn, [team_id])).get(team_id)
        await conn.execute(
            text(
                "INSERT INTO oncall_rotations (team_id, handover_local, time_zone, shift_days) "
                "VALUES (:team, :handover_local, :time_zone, :shift_days) "
                "ON CONFLICT (team_id) DO UPDATE SET handover_local = EXCLUDED.handover_local, "
                "time_zone = EXCLUDED.time_zone, shift_days = EXCLUDED.shift_days"
            ),
            {"team": team_id, **body.model_dump(exclude={"members"})},
        )
        await conn.execute(
            text("DELETE FROM oncall_members WHERE team_id = :team"), {"team": team_id}
        )
        await conn.execute(
            text(
                "INSERT INTO oncall_members (team_id, position, user_id) "
                "VALUES (:team, :position, :user)"
            ),
            [{"team": team_id, "position": i, "user": u} for i, u in enumerate(body.members)],
        )
        await record(
            conn,
            actor_id=actor,
            action="oncall.update",
            target_type="team",
            target_id=str(team_id),
            detail={
                "from": before[0].model_dump_json() if before else "",
                "to": body.model_dump_json(),
            },
        )
    return next(t for t in await list_on_call(request) if t.team_id == team_id)


class UndeliveredEmail(BaseModel):
    id: int
    kind: str
    subject: str
    to_addresses: list[str]
    created_at: datetime
    attempts: int
    next_attempt_at: datetime
    last_error: str | None


@router.get(
    "/outbox/undelivered",
    dependencies=[Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
)
async def undelivered_email(request: Request) -> list[UndeliveredEmail]:
    """Email still waiting to be sent, oldest first, so the Admin can see a mail outage."""
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(
            text(
                "SELECT id, kind, subject, to_addresses, created_at, attempts, next_attempt_at, "
                "last_error FROM outbox WHERE sent_at IS NULL ORDER BY id LIMIT 100"
            )
        )
        return [UndeliveredEmail.model_validate(r, from_attributes=True) for r in rows]

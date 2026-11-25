"""Runbooks: written at Resolved by the teams' engineers, reviewed by someone else, searchable."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api import access
from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import current_user_id
from infrawatch_api.events import publish
from infrawatch_api.incidents import lock_incident, runbook_approved
from infrawatch_core.lifecycle import Status
from infrawatch_core.policy import Capability, Relation, permits
from infrawatch_core.runbook import RootCause, Runbook, missing

router = APIRouter(tags=["runbooks"])
DETAIL = Depends(require(Capability.VIEW_INCIDENT_DETAIL))
LONG = 10_000


class RunbookIn(BaseModel):
    # Empty strings pass here on purpose: the core rule reports every empty field at once.
    timeline: str = Field(max_length=20_000)
    root_cause_category: RootCause
    root_cause: str = Field(max_length=LONG)
    contributing_factors: str = Field(max_length=LONG)
    remediation: str = Field(max_length=LONG)
    workaround: str = Field(max_length=LONG)
    similar_incident_ids: list[UUID] = Field(default_factory=list, max_length=20)
    none_similar: str = Field(default="", max_length=2000)


class ReviewIn(BaseModel):
    decision: Literal["approved", "returned"]
    comment: str = Field(default="", max_length=5000)


class Similar(BaseModel):
    id: UUID
    number: int
    title: str


class Review(BaseModel):
    decision: str
    reviewer: str
    reviewed_at: datetime
    comment: str


class Version(BaseModel):
    version: int
    author: str
    created_at: datetime
    timeline: str
    root_cause_category: RootCause
    root_cause: str
    contributing_factors: str
    remediation: str
    workaround: str
    similar_incidents: list[Similar]
    none_similar: str
    review: Review | None


class RunbookOut(BaseModel):
    categories: list[RootCause]
    suggested_timeline: str
    may_close: bool
    pending_version: int | None  # written for the current resolution, not yet reviewed
    versions: list[Version]


class SearchHit(BaseModel):
    incident_id: UUID
    number: int
    title: str
    service: str
    version: int
    root_cause_category: RootCause
    approved_at: datetime
    excerpt: str


async def _suggested_timeline(conn: AsyncConnection, incident_id: UUID) -> str:
    """The status history and escalations as text, for the writer to start from and edit."""
    rows = await conn.execute(
        text(
            "SELECT e.time, format('%s by %s', CASE WHEN e.from_status IS NULL "
            "THEN 'Raised' ELSE e.from_status || ' to ' || e.to_status END, u.display_name) "
            "|| coalesce(' (' || e.reason || ')', '') AS line FROM status_events e "
            "JOIN users u ON u.id = e.actor_id WHERE e.incident_id = :id "
            "UNION ALL SELECT x.escalated_at, format('Escalated from %s to %s', f.display_name, "
            "d.display_name) FROM escalations x JOIN users f ON f.id = x.from_user_id "
            "JOIN users d ON d.id = x.to_user_id WHERE x.incident_id = :id ORDER BY 1"
        ),
        {"id": incident_id},
    )
    return "\n".join(f"{r.time:%Y-%m-%d %H:%M} UTC  {r.line}" for r in rows)


async def _versions(conn: AsyncConnection, incident_id: UUID) -> list[Version]:
    rows = (
        await conn.execute(
            text(
                "SELECT v.*, a.display_name AS author, r.decision, r.reviewed_at, r.comment, "
                "rv.display_name AS reviewer FROM runbook_versions v "
                "JOIN users a ON a.id = v.author_id "
                "LEFT JOIN runbook_reviews r ON r.version_id = v.id "
                "LEFT JOIN users rv ON rv.id = r.reviewer_id "
                "WHERE v.incident_id = :id ORDER BY v.version"
            ),
            {"id": incident_id},
        )
    ).all()
    linked = {u for r in rows for u in r.similar_incident_ids}
    similar = {
        s.id: Similar.model_validate(s, from_attributes=True)
        for s in await conn.execute(
            text("SELECT id, number, title FROM incidents WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": list(linked)},
        )
    }
    return [
        Version(
            **{k: getattr(r, k) for k in Version.model_fields if hasattr(r, k)},
            similar_incidents=[similar[i] for i in r.similar_incident_ids if i in similar],
            review=Review.model_validate(r, from_attributes=True) if r.decision else None,
        )
        for r in rows
    ]


@router.get("/incidents/{incident_id}/runbook", dependencies=[DETAIL])
async def get_runbook(incident_id: UUID, request: Request) -> RunbookOut:
    async with request.app.state.engine.connect() as conn:
        latest, _, decision = await _latest(conn, incident_id)
        return RunbookOut(
            categories=list(RootCause),
            pending_version=latest if latest and decision is None else None,
            suggested_timeline=await _suggested_timeline(conn, incident_id),
            may_close=await runbook_approved(conn, incident_id),
            versions=await _versions(conn, incident_id),
        )


async def _latest(conn: AsyncConnection, incident_id: UUID) -> tuple[int, UUID | None, str | None]:
    """The latest version written since the incident's latest resolution: number, author, decision.

    Number is 0 and the rest None when nothing has been written for this resolution yet.
    """
    row = (
        await conn.execute(
            text(
                "SELECT v.version, v.author_id, r.decision FROM runbook_versions v "
                "LEFT JOIN runbook_reviews r ON r.version_id = v.id WHERE v.incident_id = :id "
                "AND v.created_at > (SELECT max(time) FROM status_events "
                "WHERE incident_id = :id AND to_status = 'resolved') "
                "ORDER BY v.version DESC LIMIT 1"
            ),
            {"id": incident_id},
        )
    ).first()
    return (row.version, row.author_id, row.decision) if row else (0, None, None)


@router.post("/incidents/{incident_id}/runbook", status_code=status.HTTP_201_CREATED)
async def submit_runbook(
    incident_id: UUID,
    body: RunbookIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> dict[str, int]:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        current, relation = await lock_incident(conn, incident_id, actor)
        # The engineers of every team working the incident count as its resolvers.
        if not permits(roles, Capability.WRITE_RUNBOOK, Relation(resolver=relation.team_member)):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Only an engineer on a team working this incident may write its runbook",
            )
        if current is not Status.RESOLVED:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "A runbook is written once it is Resolved"
            )
        gaps = missing(
            Runbook(
                body.timeline,
                body.root_cause,
                body.contributing_factors,
                body.remediation,
                body.workaround,
                [str(i) for i in body.similar_incident_ids],
                body.none_similar,
            )
        )
        if gaps:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                f"Every field is required; empty: {', '.join(g.replace('_', ' ') for g in gaps)}",
            )
        if incident_id in body.similar_incident_ids:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "An incident cannot be similar to itself"
            )
        known = await conn.scalar(
            text("SELECT count(*) FROM incidents WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": body.similar_incident_ids},
        )
        if known != len(set(body.similar_incident_ids)):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "A similar incident does not exist"
            )
        latest, _, decision = await _latest(conn, incident_id)
        if latest and decision is None:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Version {latest} is waiting for review")
        if decision == "approved":
            raise HTTPException(
                status.HTTP_409_CONFLICT, "This resolution's runbook is already approved"
            )
        version: int = await conn.scalar(
            text(
                "INSERT INTO runbook_versions (incident_id, version, author_id, timeline, "
                "root_cause_category, root_cause, contributing_factors, remediation, workaround, "
                "similar_incident_ids, none_similar) SELECT :id, coalesce(max(version), 0) + 1, "
                ":actor, :timeline, :root_cause_category, :root_cause, :contributing_factors, "
                ":remediation, :workaround, CAST(:similar_incident_ids AS uuid[]), :none_similar "
                "FROM runbook_versions WHERE incident_id = :id RETURNING version"
            ),
            {"id": incident_id, "actor": actor, **body.model_dump()},
        )
        await record(
            conn,
            actor_id=actor,
            action="runbook.submit",
            target_type="incident",
            target_id=str(incident_id),
            detail={"version": str(version), "category": body.root_cause_category.value},
        )
        await publish(conn, incident_id, "runbook")
    return {"version": version}


@router.post("/incidents/{incident_id}/runbook/{version}/review")
async def review_runbook(
    incident_id: UUID,
    version: int,
    body: ReviewIn,
    request: Request,
    actor: Annotated[UUID, Depends(current_user_id)],
) -> dict[str, str]:
    roles = await access.load_roles(request, actor)
    async with request.app.state.engine.begin() as conn:
        current, relation = await lock_incident(conn, incident_id, actor)
        if not permits(roles, Capability.APPROVE_RUNBOOK, Relation(lead=relation.lead)):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Only the Incident Commander or a lead of a team on this incident may review",
            )
        if current is not Status.RESOLVED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only a Resolved incident's runbook")
        latest, author, decision = await _latest(conn, incident_id)
        if version != latest:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only the latest version for this resolution is reviewed"
            )
        if decision is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Version {version} was already reviewed")
        if author == actor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "You wrote this version; someone else must review it"
            )
        comment = body.comment.strip()
        if body.decision == "returned" and not comment:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Say what to change when returning it"
            )
        await conn.execute(
            text(
                "INSERT INTO runbook_reviews (version_id, decision, reviewer_id, comment) "
                "SELECT id, :decision, :actor, :comment FROM runbook_versions "
                "WHERE incident_id = :id AND version = :version"
            ),
            {
                "id": incident_id,
                "version": version,
                "decision": body.decision,
                "actor": actor,
                "comment": comment,
            },
        )
        await record(
            conn,
            actor_id=actor,
            action=f"runbook.{'approve' if body.decision == 'approved' else 'return'}",
            target_type="incident",
            target_id=str(incident_id),
            detail={"version": str(version), "comment": comment},
        )
        await publish(conn, incident_id, "runbook")
    return {"decision": body.decision}


@router.get("/runbooks/search", dependencies=[DETAIL])
async def search_runbooks(
    request: Request,
    q: Annotated[str | None, Query(max_length=200)] = None,
    category: RootCause | None = None,
) -> list[SearchHit]:
    """The latest approved version of each incident's runbook, best match first."""
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(
            text(
                "WITH approved AS (SELECT DISTINCT ON (v.incident_id) v.*, r.reviewed_at "
                "FROM runbook_versions v JOIN runbook_reviews r ON r.version_id = v.id "
                "AND r.decision = 'approved' ORDER BY v.incident_id, v.version DESC) "
                "SELECT a.incident_id, i.number, i.title, s.name AS service, a.version, "
                "a.root_cause_category, a.reviewed_at AS approved_at, "
                # Plain text excerpt around the match: no markup ever comes from the server.
                "ts_headline('english', a.root_cause || ' ' || a.remediation, query, "
                '\'StartSel="", StopSel="", MaxWords=40, MinWords=15\') AS excerpt '
                "FROM approved a JOIN incidents i ON i.id = a.incident_id "
                "JOIN services s ON s.id = i.service_id, "
                "websearch_to_tsquery('english', coalesce(:q, '')) AS query "
                "WHERE (CAST(:q AS text) IS NULL OR a.search @@ query) "
                "AND (CAST(:category AS text) IS NULL OR a.root_cause_category = :category) "
                "ORDER BY ts_rank(a.search, query) DESC, a.reviewed_at DESC LIMIT 50"
            ),
            {"q": (q or "").strip() or None, "category": category},
        )
        return [SearchHit.model_validate(r, from_attributes=True) for r in rows]

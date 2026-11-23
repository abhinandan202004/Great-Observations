"""Alert drafts for Production Support to raise or dismiss, and the rules that create them."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.incidents import Detail, FiredAlert, RaiseIn, load_detail, open_incident
from infrawatch_core.alerting import Comparator
from infrawatch_core.lifecycle import Severity
from infrawatch_core.policy import Capability

router = APIRouter(tags=["alerting"])
RAISER = Depends(require(Capability.RAISE_INCIDENT))


class Draft(FiredAlert):
    id: UUID
    service: str
    severity: Severity


class DraftRaiseIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    impact: str = Field(min_length=1, max_length=2000)
    description: str = Field(min_length=1, max_length=10000)
    severity: Severity


class AlertRule(BaseModel):
    id: UUID
    name: str
    service: str
    metric: str
    comparator: Comparator
    threshold: float
    duration_seconds: int
    severity: Severity
    enabled: bool


class AlertRuleIn(BaseModel):
    threshold: float = Field(allow_inf_nan=False)
    duration_seconds: int = Field(ge=0, le=24 * 60 * 60)
    severity: Severity
    enabled: bool


DRAFTS = (
    "SELECT a.id, s.name AS service, a.severity, r.name AS rule, a.metric, r.comparator, "
    "r.threshold, a.breach_started_at, a.last_fired_at, a.fire_count, a.snapshot FROM alerts a "
    "JOIN alert_rules r ON r.id = a.rule_id JOIN services s ON s.id = a.service_id "
    "WHERE a.state = 'draft'"
)
RULES = (
    "SELECT r.id, r.name, s.name AS service, r.metric, r.comparator, r.threshold, "
    "r.duration_seconds, r.severity, r.enabled FROM alert_rules r "
    "JOIN services s ON s.id = r.service_id"
)


async def _locked_draft(conn: AsyncConnection, alert_id: UUID) -> Draft:
    row = (
        await conn.execute(text(f"{DRAFTS} AND a.id = :id FOR UPDATE OF a"), {"id": alert_id})
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No open draft with that id")
    return Draft.model_validate(row, from_attributes=True)


@router.get("/drafts", dependencies=[RAISER])
async def list_drafts(request: Request) -> list[Draft]:
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(text(f"{DRAFTS} ORDER BY a.fired_at DESC"))
        return [Draft.model_validate(r, from_attributes=True) for r in rows]


@router.post("/drafts/{alert_id}/raise", status_code=status.HTTP_201_CREATED)
async def raise_draft(
    alert_id: UUID,
    body: DraftRaiseIn,
    request: Request,
    actor: Annotated[UUID, RAISER],
) -> Detail:
    async with request.app.state.engine.begin() as conn:
        draft = await _locked_draft(conn, alert_id)
        incident_id = await open_incident(
            conn, RaiseIn(**body.model_dump(), service=draft.service), actor, alert_id
        )
        await conn.execute(
            text(
                "UPDATE alerts SET state = 'raised', incident_id = :incident, decided_by = :actor, "
                "decided_at = now() WHERE id = :id"
            ),
            {"incident": incident_id, "actor": actor, "id": alert_id},
        )
        return await load_detail(conn, incident_id)


@router.post("/drafts/{alert_id}/dismiss")
async def dismiss_draft(
    alert_id: UUID, request: Request, actor: Annotated[UUID, RAISER]
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        draft = await _locked_draft(conn, alert_id)
        await conn.execute(
            text(
                "UPDATE alerts SET state = 'dismissed', decided_by = :actor, decided_at = now() "
                "WHERE id = :id"
            ),
            {"actor": actor, "id": alert_id},
        )
        await record(
            conn,
            actor_id=actor,
            action="alert.dismiss",
            target_type="alert",
            target_id=str(alert_id),
            detail={"rule": draft.rule, "service": draft.service},
        )
    return {"id": str(alert_id)}


@router.get("/alert-rules", dependencies=[Depends(require(Capability.VIEW_TELEMETRY))])
async def list_rules(request: Request) -> list[AlertRule]:
    async with request.app.state.engine.connect() as conn:
        rows = await conn.execute(text(f"{RULES} ORDER BY r.name"))
        return [AlertRule.model_validate(r, from_attributes=True) for r in rows]


@router.put("/alert-rules/{rule_id}")
async def update_rule(
    rule_id: UUID,
    body: AlertRuleIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
) -> AlertRule:
    async with request.app.state.engine.begin() as conn:
        before = (
            await conn.execute(text(f"{RULES} WHERE r.id = :id FOR UPDATE OF r"), {"id": rule_id})
        ).first()
        if before is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such rule")
        await conn.execute(
            text(
                "UPDATE alert_rules SET threshold = :threshold, "
                "duration_seconds = :duration_seconds, severity = :severity, enabled = :enabled "
                "WHERE id = :id"
            ),
            {**body.model_dump(), "id": rule_id},
        )
        changed = body.model_dump(mode="json")
        await record(
            conn,
            actor_id=actor,
            action="alert_rule.update",
            target_type="alert_rule",
            target_id=str(rule_id),
            detail={
                "from": str({k: getattr(before, k) for k in changed}),
                "to": str(changed),
            },
        )
        after = (await conn.execute(text(f"{RULES} WHERE r.id = :id"), {"id": rule_id})).one()
        return AlertRule.model_validate(after, from_attributes=True)

"""Access requests and accounts: anyone may ask for access; an admin creates or approves them."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from infrawatch_api.access import require
from infrawatch_api.audit import record
from infrawatch_api.auth import hash_password
from infrawatch_core.policy import Capability
from infrawatch_core.roles import Role

router = APIRouter(tags=["accounts"])
ADMIN = Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))


class AccessRequestIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    display_name: str = Field(min_length=1, max_length=100)


class ApprovalIn(BaseModel):
    role: Role
    password: str = Field(min_length=12, max_length=256)


class UserIn(ApprovalIn):
    email: str = Field(min_length=3, max_length=254)
    display_name: str = Field(min_length=1, max_length=100)


async def _create_user(
    conn: AsyncConnection, email: str, display_name: str, body: ApprovalIn
) -> UUID:
    taken = (
        await conn.execute(text("SELECT 1 FROM users WHERE email = :email"), {"email": email})
    ).first()
    if taken is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    user_id: UUID = (
        await conn.execute(
            text(
                "INSERT INTO users (email, display_name, password_hash) "
                "VALUES (:email, :display_name, :hash) RETURNING id"
            ),
            {"email": email, "display_name": display_name, "hash": hash_password(body.password)},
        )
    ).scalar_one()
    await conn.execute(
        text("INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)"),
        {"user_id": user_id, "role": body.role.value},
    )
    return user_id


@router.post("/access-requests", status_code=status.HTTP_201_CREATED)
async def request_access(body: AccessRequestIn, request: Request) -> dict[str, str]:
    # shortcut: no rate limit or duplicate check; an admin sees every request and decides.
    async with request.app.state.engine.begin() as conn:
        request_id = (
            await conn.execute(
                text(
                    "INSERT INTO access_requests (email, display_name) "
                    "VALUES (:email, :display_name) RETURNING id"
                ),
                body.model_dump(),
            )
        ).scalar_one()
        await record(
            conn,
            actor_id=None,
            action="access_request.create",
            target_type="access_request",
            target_id=str(request_id),
        )
    return {"id": str(request_id)}


@router.get("/access-requests", dependencies=[ADMIN])
async def pending_requests(request: Request) -> list[dict[str, str]]:
    async with request.app.state.engine.connect() as conn:
        rows = (
            await conn.execute(
                text(
                    "SELECT id, email, display_name, requested_at FROM access_requests "
                    "WHERE status = 'pending' ORDER BY requested_at"
                )
            )
        ).all()
    return [
        {
            "id": str(row.id),
            "email": row.email,
            "display_name": row.display_name,
            "requested_at": row.requested_at.isoformat(),
        }
        for row in rows
    ]


@router.post("/access-requests/{request_id}/approve", status_code=status.HTTP_201_CREATED)
async def approve_request(
    request_id: UUID,
    body: ApprovalIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        asked = (
            await conn.execute(
                text(
                    "SELECT email, display_name, status FROM access_requests "
                    "WHERE id = :id FOR UPDATE"
                ),
                {"id": request_id},
            )
        ).first()
        if asked is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No such request")
        if asked.status != "pending":
            raise HTTPException(status.HTTP_409_CONFLICT, "This request was already decided")
        user_id = await _create_user(conn, asked.email, asked.display_name, body)
        await conn.execute(
            text(
                "UPDATE access_requests SET status = 'approved', decided_at = now(), "
                "decided_by = :actor WHERE id = :id"
            ),
            {"actor": actor, "id": request_id},
        )
        await record(
            conn,
            actor_id=actor,
            action="access_request.approve",
            target_type="user",
            target_id=str(user_id),
            detail={"role": body.role.value},
        )
    return {"id": str(user_id)}


@router.post("/access-requests/{request_id}/reject")
async def reject_request(
    request_id: UUID,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        updated = (
            await conn.execute(
                text(
                    "UPDATE access_requests SET status = 'rejected', decided_at = now(), "
                    "decided_by = :actor WHERE id = :id AND status = 'pending' RETURNING id"
                ),
                {"actor": actor, "id": request_id},
            )
        ).first()
        if updated is None:
            raise HTTPException(status.HTTP_409_CONFLICT, "No pending request with that id")
        await record(
            conn,
            actor_id=actor,
            action="access_request.reject",
            target_type="access_request",
            target_id=str(request_id),
        )
    return {"id": str(request_id)}


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserIn,
    request: Request,
    actor: Annotated[UUID, Depends(require(Capability.MANAGE_USERS_TEAMS_RULES))],
) -> dict[str, str]:
    async with request.app.state.engine.begin() as conn:
        user_id = await _create_user(conn, body.email, body.display_name, body)
        await record(
            conn,
            actor_id=actor,
            action="user.create",
            target_type="user",
            target_id=str(user_id),
            detail={"role": body.role.value},
        )
    return {"id": str(user_id)}

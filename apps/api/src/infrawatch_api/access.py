"""Who is calling, and whether the permission matrix lets them through."""

from collections.abc import Awaitable, Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import text

from infrawatch_api.auth import current_user_id
from infrawatch_core.policy import Capability, allows
from infrawatch_core.roles import Role


async def load_roles(request: Request, user_id: UUID) -> frozenset[Role]:
    async with request.app.state.engine.connect() as conn:
        rows = (
            await conn.execute(
                text("SELECT role FROM user_roles WHERE user_id = :id"), {"id": user_id}
            )
        ).all()
    # shortcut: roles only; team lead and team scopes are checked from M4, when incidents exist.
    return frozenset(Role(row.role) for row in rows)


def require(capability: Capability) -> Callable[..., Awaitable[UUID]]:
    async def check(request: Request, user_id: Annotated[UUID, Depends(current_user_id)]) -> UUID:
        if not allows(await load_roles(request, user_id), capability):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Your role may not do this")
        return user_id

    return check

"""``python -m infrawatch_api.seed``: load the demo data into ``DATABASE_URL``.

Idempotent: rows that already exist are left untouched, so it is safe to run repeatedly.
"""

import asyncio
import os
from typing import NamedTuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from infrawatch_core.roles import Role


class DemoUser(NamedTuple):
    email: str
    display_name: str
    role: Role
    team: str | None = None
    is_lead: bool = False


class DemoService(NamedTuple):
    name: str
    team: str
    description: str


PAYMENTS = "Payments Platform"
INFRA = "Core Infrastructure"

TEAMS = {
    PAYMENTS: "payments-team@infrawatch.local",
    INFRA: "infra-team@infrawatch.local",
}

USERS = (
    DemoUser("support@infrawatch.local", "Demo Production Support", Role.PRODUCTION_SUPPORT),
    DemoUser("developer@infrawatch.local", "Demo Developer", Role.DEVELOPER, PAYMENTS, True),
    DemoUser("sre@infrawatch.local", "Demo SRE", Role.SRE, INFRA, True),
    DemoUser("admin@infrawatch.local", "Demo Admin", Role.ADMIN),
    DemoUser("commander@infrawatch.local", "Demo Incident Commander", Role.INCIDENT_COMMANDER),
    DemoUser("comms@infrawatch.local", "Demo Comms", Role.COMMS),
    DemoUser("viewer@infrawatch.local", "Demo Read-only Viewer", Role.VIEWER),
    DemoUser("stakeholder@infrawatch.local", "Demo Business Stakeholder", Role.STAKEHOLDER),
)

SERVICES = (
    DemoService("checkout", PAYMENTS, "Demo checkout service, run by the demo app."),
    DemoService(
        "payment-gateway",
        PAYMENTS,
        "Downstream dependency of checkout; target of the dependency-latency fault.",
    ),
    DemoService(
        "demo-host", INFRA, "Host running the demo app; metrics reported by the collector agent."
    ),
)


async def seed(database_url: str) -> None:
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO teams (name, group_email) VALUES (:name, :group_email) "
                "ON CONFLICT (name) DO NOTHING"
            ),
            [{"name": name, "group_email": email} for name, email in TEAMS.items()],
        )
        await conn.execute(
            text(
                "INSERT INTO users (email, display_name) VALUES (:email, :display_name) "
                "ON CONFLICT (email) DO NOTHING"
            ),
            [{"email": u.email, "display_name": u.display_name} for u in USERS],
        )
        await conn.execute(
            text(
                "INSERT INTO user_roles (user_id, role) "
                "SELECT id, :role FROM users WHERE email = :email ON CONFLICT DO NOTHING"
            ),
            [{"email": u.email, "role": u.role.value} for u in USERS],
        )
        await conn.execute(
            text(
                "INSERT INTO memberships (user_id, team_id, is_lead) "
                "SELECT u.id, t.id, :is_lead FROM users u CROSS JOIN teams t "
                "WHERE u.email = :email AND t.name = :team ON CONFLICT DO NOTHING"
            ),
            [{"email": u.email, "team": u.team, "is_lead": u.is_lead} for u in USERS if u.team],
        )
        await conn.execute(
            text(
                "INSERT INTO services (name, team_id, description) "
                "SELECT :name, id, :description FROM teams WHERE name = :team "
                "ON CONFLICT (name) DO NOTHING"
            ),
            [s._asdict() for s in SERVICES],
        )
    await engine.dispose()


def main() -> None:
    asyncio.run(seed(os.environ["DATABASE_URL"]))
    print(f"Seeded {len(TEAMS)} teams, {len(USERS)} users and {len(SERVICES)} services.")


if __name__ == "__main__":
    main()

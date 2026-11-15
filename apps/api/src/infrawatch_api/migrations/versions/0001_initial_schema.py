"""Initial schema: extensions, application-role privileges, identity and service catalogue.

Revision ID: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Frozen copy of infrawatch_core.roles.Role; migrations must not change when the enum does.
ROLES = (
    "production_support",
    "developer",
    "sre",
    "admin",
    "incident_commander",
    "comms",
    "viewer",
    "stakeholder",
)


def upgrade() -> None:
    # The database init script already created both as superuser; restated so the schema
    # declares what it needs and fails loudly on a database without them.
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute("GRANT USAGE ON SCHEMA public TO infrawatch_app")
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO infrawatch_app"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        "GRANT USAGE, SELECT ON SEQUENCES TO infrawatch_app"
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("group_email", sa.Text, nullable=False, unique=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("display_name", sa.Text, nullable=False),
    )
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id", sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("role", sa.Text, primary_key=True),
        sa.CheckConstraint(
            "role IN (" + ", ".join(f"'{role}'" for role in ROLES) + ")", name="ck_user_roles_role"
        ),
    )
    op.create_table(
        "memberships",
        sa.Column(
            "user_id", sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "team_id", sa.Uuid, sa.ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("is_lead", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "services",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
    )


def downgrade() -> None:
    for table in ("services", "memberships", "user_roles", "users", "teams"):
        op.drop_table(table)

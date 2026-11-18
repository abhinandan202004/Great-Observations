"""Incidents, their status history and the teams working on them.

Revision ID: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATUSES = (
    "'raised', 'acknowledged', 'investigating', 'mitigating', 'monitoring', 'resolved', 'closed'"
)


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("number", sa.BigInteger, sa.Identity(), nullable=False, unique=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("impact", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("severity", sa.Text, nullable=False),
        sa.Column("service_id", sa.Uuid, sa.ForeignKey("services.id"), nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="raised"),
        sa.Column("caller_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "raised_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("severity IN ('P1', 'P2', 'P3', 'P4')", name="ck_incidents_severity"),
        sa.CheckConstraint(f"status IN ({STATUSES})", name="ck_incidents_status"),
    )

    op.create_table(
        "status_events",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("actor_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_status", sa.Text, nullable=True),
        sa.Column("to_status", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        # A reopen points at the Resolved event it rejects.
        sa.Column("reopens", sa.BigInteger, sa.ForeignKey("status_events.id"), nullable=True),
        sa.CheckConstraint(f"to_status IN ({STATUSES})", name="ck_status_events_to_status"),
    )
    op.create_index("ix_status_events_incident", "status_events", ["incident_id", "id"])
    # Status history feeds the SLA timers, so it is written once like the audit log.
    op.execute("REVOKE ALL ON status_events FROM infrawatch_app")
    op.execute("GRANT SELECT, INSERT ON status_events TO infrawatch_app")

    op.create_table(
        "team_tasks",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("assignee_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=True),
        sa.UniqueConstraint("incident_id", "team_id", name="uq_team_tasks_incident_team"),
    )


def downgrade() -> None:
    op.drop_table("team_tasks")
    op.drop_table("status_events")
    op.drop_table("incidents")

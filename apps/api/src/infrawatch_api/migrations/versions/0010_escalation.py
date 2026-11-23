"""Escalation timers on the SLA policy, and the record of each escalation.

Revision ID: 0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # NULL means the severity never escalates.
    op.add_column("sla_policies", sa.Column("escalate_minutes", sa.Integer, nullable=True))
    op.create_check_constraint(
        "ck_sla_policies_escalate",
        "sla_policies",
        "escalate_minutes IS NULL OR escalate_minutes > 0",
    )
    # context.md section 5.1 for P1 and P2; P3 and P4 as agreed for M6.
    op.execute(
        "UPDATE sla_policies SET escalate_minutes = CASE severity "
        "WHEN 'P1' THEN 10 WHEN 'P2' THEN 10 WHEN 'P3' THEN 60 END"
    )

    op.create_table(
        "escalations",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("step", sa.Integer, nullable=False),
        sa.Column("from_user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("to_user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "escalated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        # A second sweep racing the first cannot record the same step twice.
        sa.UniqueConstraint("incident_id", "team_id", "step", name="uq_escalations_step"),
    )
    op.execute("REVOKE ALL ON escalations FROM infrawatch_app")
    op.execute("GRANT SELECT, INSERT ON escalations TO infrawatch_app")


def downgrade() -> None:
    op.drop_table("escalations")
    op.drop_constraint("ck_sla_policies_escalate", "sla_policies")
    op.drop_column("sla_policies", "escalate_minutes")

"""Team task checklists and the Admin-configurable SLA policy.

Revision ID: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "checklist_items",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", sa.Uuid, sa.ForeignKey("team_tasks.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("done", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    sla = op.create_table(
        "sla_policies",
        sa.Column("severity", sa.Text, primary_key=True),
        sa.Column("acknowledge_minutes", sa.Integer, nullable=False),
        sa.Column("resolve_minutes", sa.Integer, nullable=False),
        sa.CheckConstraint("severity IN ('P1', 'P2', 'P3', 'P4')", name="ck_sla_policies_severity"),
        sa.CheckConstraint(
            "acknowledge_minutes > 0 AND resolve_minutes > 0", name="ck_sla_policies_positive"
        ),
    )
    # The defaults from context.md section 5.1; an Admin changes them in the app.
    op.bulk_insert(
        sla,
        [
            {"severity": "P1", "acknowledge_minutes": 5, "resolve_minutes": 4 * 60},
            {"severity": "P2", "acknowledge_minutes": 15, "resolve_minutes": 8 * 60},
            {"severity": "P3", "acknowledge_minutes": 60, "resolve_minutes": 3 * 24 * 60},
            {"severity": "P4", "acknowledge_minutes": 4 * 60, "resolve_minutes": 7 * 24 * 60},
        ],
    )


def downgrade() -> None:
    op.drop_table("sla_policies")
    op.drop_table("checklist_items")

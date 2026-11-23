"""Static alert rules, and the alerts they raise as drafts for Production Support.

Revision ID: 0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("service_id", sa.Uuid, sa.ForeignKey("services.id"), nullable=False),
        sa.Column("metric", sa.Text, nullable=False),
        sa.Column("comparator", sa.Text, nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("duration_seconds", sa.Integer, nullable=False),
        sa.Column("severity", sa.Text, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.CheckConstraint("comparator IN ('above', 'below')", name="ck_alert_rules_comparator"),
        sa.CheckConstraint("duration_seconds >= 0", name="ck_alert_rules_duration"),
        sa.CheckConstraint("severity IN ('P1', 'P2', 'P3', 'P4')", name="ck_alert_rules_severity"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rule_id", sa.Uuid, sa.ForeignKey("alert_rules.id"), nullable=False),
        # Copied from the rule at firing time, so a later rule edit does not rewrite history.
        sa.Column("service_id", sa.Uuid, sa.ForeignKey("services.id"), nullable=False),
        sa.Column("metric", sa.Text, nullable=False),
        sa.Column("severity", sa.Text, nullable=False),
        sa.Column("breach_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_fired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fire_count", sa.Integer, nullable=False, server_default="1"),
        # The metric points from the breach window, frozen when the alert first fired.
        sa.Column("snapshot", postgresql.JSONB, nullable=False),
        sa.Column("state", sa.Text, nullable=False, server_default="draft"),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=True),
        sa.Column("decided_by", sa.Uuid, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("state IN ('draft', 'raised', 'dismissed')", name="ck_alerts_state"),
        sa.CheckConstraint(
            "(state = 'raised') = (incident_id IS NOT NULL)", name="ck_alerts_raised_incident"
        ),
    )
    # At most one draft per rule: repeated firings fold into it.
    op.create_index(
        "uq_alerts_one_draft_per_rule",
        "alerts",
        ["rule_id"],
        unique=True,
        postgresql_where=sa.text("state = 'draft'"),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("alert_rules")

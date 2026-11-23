"""Runbook versions and their reviews, both written once and never changed.

Revision ID: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CATEGORIES = (
    "'code_or_deploy', 'configuration', 'capacity_or_infrastructure', "
    "'dependency_or_third_party', 'data', 'security', 'process_or_human'"
)
# Weighted so a match in the root cause ranks above one in the timeline.
SEARCH = (
    "setweight(to_tsvector('english', root_cause), 'A') || "
    "setweight(to_tsvector('english', remediation || ' ' || contributing_factors), 'B') || "
    "setweight(to_tsvector('english', workaround || ' ' || timeline), 'C')"
)


def upgrade() -> None:
    op.create_table(
        "runbook_versions",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("author_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("timeline", sa.Text, nullable=False),
        sa.Column("root_cause_category", sa.Text, nullable=False),
        sa.Column("root_cause", sa.Text, nullable=False),
        sa.Column("contributing_factors", sa.Text, nullable=False),
        sa.Column("remediation", sa.Text, nullable=False),
        sa.Column("workaround", sa.Text, nullable=False),
        sa.Column("similar_incident_ids", postgresql.ARRAY(sa.Uuid), nullable=False),
        sa.Column("none_similar", sa.Text, nullable=False, server_default=""),
        sa.Column("search", postgresql.TSVECTOR, sa.Computed(SEARCH, persisted=True)),
        sa.UniqueConstraint("incident_id", "version", name="uq_runbook_versions_version"),
        sa.CheckConstraint(
            f"root_cause_category IN ({CATEGORIES})", name="ck_runbook_versions_category"
        ),
    )
    op.create_index(
        "ix_runbook_versions_search", "runbook_versions", ["search"], postgresql_using="gin"
    )
    op.create_table(
        "runbook_reviews",
        sa.Column(
            "version_id", sa.BigInteger, sa.ForeignKey("runbook_versions.id"), primary_key=True
        ),
        sa.Column("decision", sa.Text, nullable=False),
        sa.Column("reviewer_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("comment", sa.Text, nullable=False, server_default=""),
        sa.CheckConstraint(
            "decision IN ('approved', 'returned')", name="ck_runbook_reviews_decision"
        ),
    )
    # A version is the record of what was submitted and approved: it never changes afterwards.
    for table in ("runbook_versions", "runbook_reviews"):
        op.execute(f"REVOKE ALL ON {table} FROM infrawatch_app")
        op.execute(f"GRANT SELECT, INSERT ON {table} TO infrawatch_app")


def downgrade() -> None:
    op.drop_table("runbook_reviews")
    op.drop_table("runbook_versions")

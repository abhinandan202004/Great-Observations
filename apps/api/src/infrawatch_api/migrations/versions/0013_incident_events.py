"""The incident event log that live updates replay from.

Revision ID: 0013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The per-incident counter is bumped with UPDATE ... RETURNING, so the row lock gives every
    # event on one incident a unique, gap-free number in commit order.
    op.add_column(
        "incidents", sa.Column("event_seq", sa.Integer, nullable=False, server_default="0")
    )
    op.create_table(
        "incident_events",
        # Global order across incidents, for the incident list's subscription.
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("seq", sa.Integer, nullable=False),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("incident_id", "seq", name="uq_incident_events_seq"),
    )
    op.execute("REVOKE ALL ON incident_events FROM infrawatch_app")
    op.execute("GRANT SELECT, INSERT ON incident_events TO infrawatch_app")


def downgrade() -> None:
    op.drop_table("incident_events")
    op.drop_column("incidents", "event_seq")

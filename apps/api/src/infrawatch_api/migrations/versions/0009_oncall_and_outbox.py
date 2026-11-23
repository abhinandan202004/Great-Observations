"""On-call rotations, and the outbox the worker delivers email from.

Revision ID: 0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oncall_rotations",
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("teams.id"), primary_key=True),
        # Wall-clock time in time_zone, so handovers keep their local time across DST.
        sa.Column("handover_local", sa.DateTime(timezone=False), nullable=False),
        sa.Column("time_zone", sa.Text, nullable=False),
        sa.Column("shift_days", sa.Integer, nullable=False),
        sa.CheckConstraint("shift_days BETWEEN 1 AND 28", name="ck_oncall_rotations_shift_days"),
    )
    op.create_table(
        "oncall_members",
        sa.Column("team_id", sa.Uuid, sa.ForeignKey("oncall_rotations.team_id"), primary_key=True),
        sa.Column("position", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("team_id", "user_id", name="uq_oncall_members_team_user"),
    )

    op.create_table(
        "outbox",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        # Derived from the originating change; it becomes the Message-ID, so a resend after
        # a crash between sending and recording is recognisable as the same message.
        sa.Column("idempotency_key", sa.Text, nullable=False, unique=True),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=True),
        sa.Column("to_addresses", postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column("cc_addresses", postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column("subject", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
    )
    op.create_index(
        "ix_outbox_pending",
        "outbox",
        ["next_attempt_at"],
        postgresql_where=sa.text("sent_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_table("outbox")
    op.drop_table("oncall_members")
    op.drop_table("oncall_rotations")

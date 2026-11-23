"""Incident attachments: frozen metric snapshots, log excerpts, files, links and notes.

Revision ID: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

KINDS = "'metric_snapshot', 'log_excerpt', 'file', 'link', 'note'"


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", sa.Uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("created_by", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        # Snapshot points, log lines, or the link and note text, copied at attachment time.
        sa.Column("data", postgresql.JSONB, nullable=False, server_default="{}"),
        # Files only: where the bytes live in object storage, and what they are.
        sa.Column("object_key", sa.Text, nullable=True, unique=True),
        sa.Column("file_name", sa.Text, nullable=True),
        sa.Column("content_type", sa.Text, nullable=True),
        sa.Column("size_bytes", sa.Integer, nullable=True),
        sa.CheckConstraint(f"kind IN ({KINDS})", name="ck_attachments_kind"),
        sa.CheckConstraint(
            "(kind = 'file') = (object_key IS NOT NULL)", name="ck_attachments_file_object"
        ),
    )
    op.create_index("ix_attachments_incident", "attachments", ["incident_id", "created_at"])
    # Attached evidence is frozen: the app may add attachments but never change or remove one.
    op.execute("REVOKE ALL ON attachments FROM infrawatch_app")
    op.execute("GRANT SELECT, INSERT ON attachments TO infrawatch_app")


def downgrade() -> None:
    op.drop_table("attachments")

"""Password hashes, access requests and the insert-only audit log.

Revision ID: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.Text, nullable=True))

    op.create_table(
        "access_requests",
        sa.Column("id", sa.Uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column(
            "requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by", sa.Uuid, sa.ForeignKey("users.id"), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')", name="ck_access_requests_status"
        ),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("actor_id", sa.Uuid, nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("target_type", sa.Text, nullable=False),
        sa.Column("target_id", sa.Text, nullable=False),
        sa.Column("detail", postgresql.JSONB, nullable=False, server_default="{}"),
    )
    # The default privileges from 0001 would give the app role UPDATE and DELETE here.
    op.execute("REVOKE ALL ON audit_log FROM infrawatch_app")
    op.execute("GRANT SELECT, INSERT ON audit_log TO infrawatch_app")
    # A second safeguard for the owner role: the database refuses any change to the log.
    # Statement-level, so it also refuses a change that matches no rows.
    op.execute(
        """
        CREATE FUNCTION audit_log_append_only() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_append_only
            BEFORE UPDATE OR DELETE OR TRUNCATE ON audit_log
            FOR EACH STATEMENT EXECUTE FUNCTION audit_log_append_only()
        """
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_append_only()")
    op.drop_table("access_requests")
    op.drop_column("users", "password_hash")

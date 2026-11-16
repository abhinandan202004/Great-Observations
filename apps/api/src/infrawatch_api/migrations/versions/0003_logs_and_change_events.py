"""Log entries hypertable (30-day retention, full-text search) and change events.

Revision ID: 0003
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Senders generate the ids, so a batch or event resent after a lost response
    # inserts nothing twice.
    op.execute(
        """
        CREATE TABLE log_entries (
            id uuid NOT NULL,
            time timestamptz NOT NULL,
            service_id uuid NOT NULL REFERENCES services (id),
            level text NOT NULL CHECK (level IN ('debug', 'info', 'warning', 'error')),
            message text NOT NULL,
            correlation_id text,
            PRIMARY KEY (id, time)
        )
        """
    )
    op.execute("SELECT create_hypertable('log_entries', by_range('time', INTERVAL '1 day'))")
    op.execute("SELECT add_retention_policy('log_entries', INTERVAL '30 days')")
    op.execute(
        "CREATE INDEX ix_log_entries_service_level_time "
        "ON log_entries (service_id, level, time DESC)"
    )
    op.execute("CREATE INDEX ix_log_entries_correlation_id ON log_entries (correlation_id)")
    op.execute(
        "CREATE INDEX ix_log_entries_message_fts ON log_entries "
        "USING gin (to_tsvector('english', message))"
    )

    # Change events are few and are kept indefinitely, so this is a plain table.
    op.execute(
        """
        CREATE TABLE change_events (
            id uuid PRIMARY KEY,
            time timestamptz NOT NULL,
            service_id uuid NOT NULL REFERENCES services (id),
            kind text NOT NULL CHECK (kind IN ('deploy', 'config', 'feature_flag')),
            summary text NOT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_change_events_service_time ON change_events (service_id, time DESC)"
    )


def downgrade() -> None:
    op.drop_table("change_events")
    op.drop_table("log_entries")

"""Metric samples hypertable with 30-day retention.

Revision ID: 0002
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The primary key makes ingest idempotent: a batch resent after a lost response
    # (the agent retries until it sees a 2xx) inserts nothing twice.
    op.execute(
        """
        CREATE TABLE metric_samples (
            time timestamptz NOT NULL,
            service_id uuid NOT NULL REFERENCES services (id),
            metric text NOT NULL,
            value double precision NOT NULL,
            PRIMARY KEY (service_id, metric, time)
        )
        """
    )
    op.execute("SELECT create_hypertable('metric_samples', by_range('time', INTERVAL '1 day'))")
    op.execute("SELECT add_retention_policy('metric_samples', INTERVAL '30 days')")


def downgrade() -> None:
    op.drop_table("metric_samples")

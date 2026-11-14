# 0006. PostgreSQL with TimescaleDB and pgvector

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The system stores relational workflow data (incidents, runbooks, audit), time-series telemetry with a 30-day retention policy, and, from Phase 2, vector embeddings for retrieval. Running separate databases for each would increase operational load for a small, self-hostable project.

## Decision

- A single PostgreSQL instance holds all persistent data except attachments.
- **TimescaleDB** hypertables store metric samples and log entries, with retention policies enforcing the 30-day default.
- **pgvector** stores embeddings for runbooks and incidents.
- The `timescale/timescaledb-ha` image is used because it ships with both extensions; the exact image tag is pinned in the Compose file in milestone M1.
- Attachments are stored in MinIO, not in the database.

## Consequences

- One backup, one connection pool and one migration history cover all structured data.
- Telemetry write load and workflow queries share one instance; at demo scale this is acceptable, and the scale-out path (a separate telemetry store) is documented rather than built.

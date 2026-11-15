# Architecture decision records

This directory holds one record per significant decision, following the format described in [ADR 0001](0001-record-architecture-decisions.md). Records are numbered sequentially and are never deleted; a decision that changes is recorded in a new ADR that supersedes the earlier one.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-repository-layout-and-python-workspace.md) | Repository layout and Python workspace | Accepted |
| [0003](0003-pure-domain-core.md) | Pure domain core with a coverage floor | Accepted |
| [0004](0004-python-toolchain.md) | Python toolchain | Accepted |
| [0005](0005-frontend-stack.md) | Frontend stack | Accepted |
| [0006](0006-database-timescaledb-and-pgvector.md) | PostgreSQL with TimescaleDB and pgvector | Accepted |
| [0007](0007-persistence-sqlalchemy-and-alembic.md) | Persistence with SQLAlchemy and Alembic | Accepted |
| [0008](0008-job-queue-and-outbox-in-postgresql.md) | Job queue and transactional outbox in PostgreSQL | Accepted |
| [0009](0009-websockets-for-real-time-updates.md) | WebSockets for real-time updates | Accepted |
| [0010](0010-event-fan-out-with-listen-notify.md) | Event fan-out with LISTEN/NOTIFY | Accepted |
| [0011](0011-authentication-and-tokens.md) | Authentication and tokens | Accepted |
| [0012](0012-immutable-audit-log.md) | Immutable audit log | Accepted |
| [0013](0013-standalone-ticketing-with-optional-servicenow-sync.md) | Standalone ticketing with optional ServiceNow synchronisation | Accepted |
| [0014](0014-defer-full-dashboard-builder.md) | Defer the full dashboard builder to Phase 3 | Accepted |
| [0015](0015-python-collector-agent.md) | Python collector agent with a bounded on-disk buffer | Accepted |
| [0016](0016-continuous-integration-and-container-builds.md) | Continuous integration and container builds | Accepted |
| [0017](0017-object-storage-rustfs.md) | Object storage with RustFS | Accepted |

## Template

```markdown
# NNNN. Title

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD

## Context
The forces at play and the problem to be solved.

## Decision
What has been decided, stated in full sentences.

## Consequences
What becomes easier or harder, including accepted trade-offs.
```

# 0007. Persistence with SQLAlchemy and Alembic

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The API and worker need typed, asynchronous database access and a versioned schema whose migrations can create TimescaleDB hypertables, retention policies, database roles and the audit-table grants required by G8.4.

## Decision

- **SQLAlchemy 2.0** in asynchronous mode, with the **asyncpg** driver, for database access.
- **Alembic** for schema migrations. Migrations may contain raw SQL where SQLAlchemy has no construct, such as hypertable creation, retention policies, role grants and triggers.
- **Pydantic v2** models define API request and response schemas; persistence models and API schemas are kept separate.
- Migrations run as a dedicated owner role. The application connects as a separate role with only the privileges it needs (see [ADR 0012](0012-immutable-audit-log.md)).

## Consequences

- Schema history is reproducible from a clean database, supporting G0.1.
- Separate owner and application roles add a small amount of configuration in exchange for enforceable privileges.

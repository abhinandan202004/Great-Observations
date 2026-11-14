# 0013. Standalone ticketing with optional ServiceNow synchronisation

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The product originates from an organisation where observability tooling and ServiceNow ticketing were separate. Depending on ServiceNow would make the project impossible to run from a clean clone and would place the core workflow outside the project's control.

## Decision

- InfraWatch contains its own complete incident ticketing system, which is the system of record.
- ServiceNow synchronisation is an optional Phase 3 integration through the Table API against a developer instance. When it is enabled, raising an incident creates the ServiceNow record, and status changes synchronise in both directions.
- Every synchronised operation carries an idempotency key. Failed operations are queued through the outbox ([ADR 0008](0008-job-queue-and-outbox-in-postgresql.md)) and are visible to an Admin.
- With synchronisation disabled or the instance unreachable, the application behaves identically.
- The field mapping between the InfraWatch incident model and the ServiceNow table is decided when Phase 3 begins.

## Consequences

- The whole product can be demonstrated without any external service.
- Two-way synchronisation requires conflict rules, to be defined with the field mapping in Phase 3.

# 0008. Job queue and transactional outbox in PostgreSQL

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The worker runs alert evaluation, SLA and escalation checks, email dispatch and, later, embedding and ServiceNow synchronisation. Emails must be sent exactly when an incident event commits: never for a rolled-back change, never twice for one event (G4.3, G4.4). Mail, LLM or ServiceNow failure must not block the incident workflow (design principle 2). The architecture contains no message broker.

## Decision

- Background jobs are rows in a PostgreSQL table, claimed by workers with `SELECT … FOR UPDATE SKIP LOCKED`.
- Side effects caused by a state change (emails, notifications, synchronisation) are written to an **outbox** table in the same transaction as the change. The worker delivers outbox entries, retrying with backoff, and records the outcome.
- Each outbox entry carries an idempotency key derived from the originating event, so a retry cannot produce a duplicate delivery.
- Periodic tasks (alert evaluation, SLA and escalation sweeps, staleness checks) are scheduled inside the worker at configurable intervals.

## Consequences

- No Redis or other broker is added to the deployment.
- A failed side effect is visible as a pending or failed outbox row instead of being lost, and never rolls back the workflow change.
- Throughput is bounded by PostgreSQL, which is ample at demo scale; moving to a broker later is a documented scale-out step.

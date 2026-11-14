# 0012. Immutable audit log

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

Every change to incidents, status, assignments, alert rules, on-call schedules and runbooks must write an audit entry recording who, what, when, before and after (G8.3). The audit log must have no update or delete path in the API, and the database role used by the application must be unable to modify it (G8.4). Immutability enforced only by application code would not meet the second requirement.

## Decision

- Audit entries are written in the **same transaction** as the change they describe, so a change and its audit record are committed or rolled back together.
- Each entry stores the actor, the action, the entity type and identifier, a timestamp, and the before and after state as JSON.
- The application database role is granted `INSERT` and `SELECT` on the audit table and nothing else.
- A trigger rejects `UPDATE` and `DELETE` on the audit table as a second safeguard that also applies to more privileged roles.
- The API exposes audit entries read-only.
- An integration test connects as the application role and confirms that updates and deletes are refused.

## Consequences

- Audit integrity does not depend on application code being correct.
- Correcting a mistaken audit entry is impossible by design; corrections are recorded as new entries.
- Retention is indefinite, as specified, so the table grows without bound; at demo scale this is negligible.

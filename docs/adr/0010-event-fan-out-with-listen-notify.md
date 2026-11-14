# 0010. Event fan-out with LISTEN/NOTIFY

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

Incident events originate both in the API (user actions) and in the worker (escalations, SLA breaches). Both must reach the WebSocket gateway, which runs in the API process. The architecture contains no message broker.

## Decision

- Incident events are persisted in the incident event log, which is the source for WebSocket replay ([ADR 0009](0009-websockets-for-real-time-updates.md)).
- After the transaction commits, a PostgreSQL `NOTIFY` on a dedicated channel carries the incident identifier and sequence number. The gateway `LISTEN`s, reads the event from the log and forwards it to subscribed connections.
- The notification payload is a pointer, not the event itself, so the size limit on notification payloads is irrelevant and the log remains authoritative.

## Consequences

- Fan-out needs no additional infrastructure.
- A missed notification (for example during a gateway restart) is recovered through the client's sequence-based replay.
- Running several API instances works, because each instance listens independently. Very high event rates would justify a broker, which is a documented scale-out step.

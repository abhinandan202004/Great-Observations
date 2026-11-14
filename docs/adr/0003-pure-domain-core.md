# 0003. Pure domain core with a coverage floor

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The value of the product depends on rules that must never be bypassed: the seven-state incident lifecycle, caller-only closure, the runbook gate, the permission matrix, SLA timers and escalation. Acceptance check G9.1 requires an agreed coverage floor on exactly this logic, and the floor was set at 90% line and branch coverage on 2026-11-09. Logic that is interleaved with database access, HTTP handling or wall-clock time is slow and awkward to test exhaustively.

## Decision

- The state machine, permission policy, SLA calculation and escalation decisions live in `infrawatch-core` as pure functions and immutable data types.
- The package performs no I/O, does not import web, database or network libraries, and never reads the system clock; callers pass the current time explicitly.
- The API and worker load state, call the core to decide, and persist the outcome. Enforcement points in the API always delegate to the core rather than re-implementing a rule.
- CI enforces 90% line and branch coverage on `infrawatch-core` from milestone M4, when the first domain modules exist. Other packages report coverage without a blocking floor.

## Consequences

- Rules can be tested exhaustively and quickly, including time-dependent behaviour, without containers.
- A single implementation of each rule serves both the API and the worker.
- Some data must be mapped between persistence models and core types, which adds a thin translation layer.

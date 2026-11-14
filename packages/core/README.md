# infrawatch-core

Pure domain logic shared by the API and the worker: the incident state machine, the permission policy, SLA calculation and escalation decisions.

Modules in this package perform no I/O. Time is supplied by an injected clock, and persistence is the caller's responsibility. This keeps the logic deterministic and exhaustively unit-testable; the package carries the 90% line and branch coverage floor required by acceptance check G9.1 (see [ADR 0003](../../docs/adr/0003-pure-domain-core.md)).

> **Status:** package skeleton only (milestone M0). The domain modules are delivered from milestone M3 onward.

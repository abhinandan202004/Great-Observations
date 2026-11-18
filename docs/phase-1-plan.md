# InfraWatch 2.0: Phase 1 implementation plan

> **Status: approved on 2026-11-09.** Implementation is in progress; milestones M0 and M1 are implemented. Technology choices marked *(ADR)* are recorded as architecture decision records in [`docs/adr/`](adr/).

## 1. Scope

Phase 1 delivers the incident loop: every acceptance check tagged **[P1]** (44 checks), plus the release checks **G10.1** and **G10.2**, and the walkthrough recording from **G10.3**. AI features, ServiceNow synchronisation and the full dashboard builder are out of scope.

The milestones follow the agreed principle of a thin vertical slice first. Milestones M0 to M8 produce a complete, test-covered path from fault injection to caller closure. Milestones M9 and M10 broaden and harden that path.

## 2. Decisions confirmed on 2026-11-09 (open items from `context.md` section 13.2)

| # | Item | Decision |
|---|---|---|
| 1 | Who may change severity | Production Support, SRE and Incident Commander, as in the proposed permission matrix. The matrix is confirmed as written. |
| 2 | G6.3 accuracy target | **Top-3 accuracy of at least 70%** on the held-out set of injected faults. Synthetic-corpus and live-fault results are reported separately. Fixed now, before any evaluation is run. |
| 3 | G9.1 coverage floor | **90% line and branch coverage** on the core modules (state machine, permissions, SLA, escalation), enforced in CI. Other code reports coverage without a blocking floor. |
| 4 | ServiceNow field mapping | Deferred to Phase 3; not required by Phase 1. |
| 5 | Demo teams | *Payments Platform* (`payments-team@infrawatch.local`) and *Core Infrastructure* (`infra-team@infrawatch.local`). |
| 6 | Collector agent | **Python** (psutil, httpx2). Reporting interval 5 s. On-disk SQLite buffer holding at most 10,000 samples (about 2 hours 20 minutes at the default 5 s interval, which records 6 metrics per reading); on overflow the oldest samples are dropped and the drop count is itself reported as a metric. Retry with exponential backoff from 1 s to 60 s with jitter. |
| 7 | WebSocket behaviour | Every incident event carries a monotonically increasing sequence number. On reconnect (exponential backoff) the client sends its last sequence number and the server replays the missed events from the event log; if the gap exceeds the replay window the server instructs the client to refetch the full incident. Each connection has a bounded send queue of 100 messages; a client that overflows it is disconnected with a "resync required" close code. Heartbeat every 20 s. |

### Decisions for M2 (confirmed on 2026-11-16)

| Item | Decision |
|---|---|
| Ingest authentication | Bearer API keys from `.env` (`AGENT_INGEST_KEY`, later one per sender), compared in constant time by the API. Any valid key may write for any service until M3 adds key management and binds keys to services. Change events are signed with HMAC-SHA256 (M2 PR 2). |
| Demo-app telemetry | The demo app posts its own request metrics and logs to the ingest API; the agent reports host metrics only. |
| Chart freshness | The chart polls every 5 s; the WebSocket gateway arrives in M8. |
| Delivery | Three pull requests: (1) metric ingest, hypertable and agent (G1.1, G1.5); (2) demo-app telemetry, logs, change events and fault injection (G1.2, G1.4, G1.6); (3) chart with change markers and log search (G1.3 and the display side). |
| Fault injection | `python -m infrawatch_demo_app.fault <fault> [--minutes N]` calls an internal demo-app endpoint; faults stop after 5 minutes by default or on `fault stop`; one fault at a time. |
| Demo traffic | A background loop inside the demo app calls its checkout endpoint about 5 times a second. |
| Read access | Telemetry read endpoints and pages are unauthenticated until M3 puts them behind login. |
| G1.5 verification | Unit tests for the buffer and backoff, plus `scripts/check-telemetry.sh` in CI: the API is stopped for 30 s with an agent restart in the middle, and the stored samples must show no gap longer than 12 s. |

## 3. Proposed technical foundations

| Concern | Proposal | Rationale |
|---|---|---|
| Python toolchain *(ADR)* | Python 3.12, `uv`, Ruff, mypy (strict on core modules), pytest | Fast, reproducible dependency resolution; one linter and formatter. |
| API persistence *(ADR)* | SQLAlchemy 2.0 (async) with asyncpg, Alembic migrations, Pydantic v2 | Mature, typed, works with Timescale and pgvector extensions. |
| Database image *(ADR)* | `timescale/timescaledb-ha` (includes pgvector) | One image provides both required extensions. |
| Worker and jobs *(ADR)* | PostgreSQL-backed job queue (`SELECT … FOR UPDATE SKIP LOCKED`) plus a transactional outbox for emails and notifications | No additional infrastructure such as Redis; jobs are created in the same transaction as the change that causes them, so nothing is lost or sent twice. |
| Event fan-out *(ADR)* | PostgreSQL `LISTEN/NOTIFY` from worker and API to the WebSocket gateway | Sufficient at demo scale; scale-out path (a message broker) documented, not built. |
| Authentication *(ADR)* | Argon2id password hashing; short-lived access JWT (15 min) with rotating refresh token | Meets G8.2; expiry is testable. |
| Audit immutability *(ADR)* | Audit rows written in the same transaction as the change; the application's database role has `INSERT` and `SELECT` only on the audit table; a trigger rejects `UPDATE` and `DELETE` as a second safeguard | Meets G8.4 at the database layer, not only in the API. |
| Core logic structure | State machine, permission policy, SLA and escalation as pure modules with an injected clock, no I/O | Exhaustively unit-testable; carries the 90% floor. |
| Frontend *(ADR)* | Next.js (App Router, TypeScript), Apache ECharts for time series and change markers, `react-grid-layout` for the panel builder, Vitest, Playwright | ECharts renders markers and large series efficiently; grid layout covers G2.2 without a custom builder. |
| Log search | PostgreSQL full-text index on the message plus indexed service, level and time filters | No separate search engine needed at demo scale. |
| Ingest authentication | Per-agent API keys for telemetry; HMAC-SHA256 signatures for the change-event webhook | Meets the authenticated webhook requirement. |
| Test timing | A configurable "drill" profile that shortens alert evaluation, SLA and escalation timers | Lets E2E and escalation tests finish in minutes without changing code. |

## 4. Milestones

Each milestone ends in a demonstrable state and a set of acceptance checks that can be verified. A check is ticked only after it has actually been verified. Every milestone includes its own user interface surfaces, its unit and integration tests, its audit entries and its additions to the permission matrix test.

### M0. Repository foundation and CI

- Monorepo layout as in `context.md` section 15.1; `.gitattributes` for consistent line endings; `.env.example`.
- ADRs for the decisions in section 3, and for the decisions already agreed (WebSockets, standalone ticketing, Phase 3 dashboard builder).
- GitHub Actions workflow: lint, type-check, unit tests and Docker builds for each app; secret scanning (gitleaks).
- Branch protection on `main` requiring the workflow to pass. This setting is applied in GitHub by the repository owner; the plan supplies the exact settings.

**Verifies:** G9.4. Partially G8.2 (no committed secrets).

### M1. Environment skeleton

- Compose file with all eight services (`web`, `api`, `worker`, `db`, `objectstore`, `mailpit`, `agent`, `demo-app`), each with a health endpoint and a Compose health check. Object storage is RustFS, replacing the archived MinIO ([ADR 0017](adr/0017-object-storage-rustfs.md)); a one-shot `migrate` service applies migrations before the API starts.
- Initial migration enabling TimescaleDB and pgvector; database roles for migration owner and application.
- Seed command: one demo user per role, the two demo teams with group emails and leads, the demo service catalogue.

**Verifies:** G0.1, G0.2, G0.3.

### M2. Telemetry ingest and first chart

- Ingest endpoints for metric samples, log entries and change events; hypertables with 30-day retention policies.
- Collector agent with the buffer and retry policy in section 2; documented buffer limits.
- Demo application emitting latency, error rate, request rate and structured logs with correlation IDs.
- Fault-injection command: `cpu-spike`, `error-burst`, `bad-deploy` (emits a change event), `dependency-latency`.
- One service chart with change markers, and a log search view.

**Verifies:** G1.1 to G1.6.

### M3. Identity, RBAC and audit foundation

- Local accounts, login, token refresh and expiry.
- Roles, team memberships with the team-lead attribute, and the permission policy module encoding the confirmed matrix.
- Audit table, insert-only role and trigger; audit writer used by every mutating endpoint.
- Permission matrix test harness that runs every endpoint against all eight roles.

**Verifies:** G8.2 (complete), G8.4. Starts G8.1 and G8.3; both grow in each later milestone.

### M4. Incident lifecycle core

- Incident model, seven-state machine, transition endpoint rejecting every undefined transition, regression with a required reason.
- Raise from scratch with severity P1 to P4; severity change restricted per the matrix.
- Parallel team tasks with assignee and checklist under one shared status; assignment limited to the lead's own team.
- SLA policy (Admin-configurable), timers derived from status events, remaining time and breach flags.
- Caller-only Close (403 for everyone else), gated on an approved runbook; until M7 the gate cannot be satisfied, so closure is always refused. Caller rejection returns the incident to Investigating with a reason linked to the earlier resolution.
- Status-and-impact-only view for stakeholders and read-only viewers.
- Coverage floor enforced in CI from this milestone onward.

**Verifies:** G3.2 to G3.8, G8.5. Partially G3.1 (raise from scratch, without attachments).

### M5. Static alerts and drafts

- Static threshold rules with a duration condition, evaluated by the worker.
- A firing alert creates a draft incident pre-filled with service, time range and a frozen metric snapshot; no notification until Production Support raises it.
- Deduplication by rule and service into the open draft or incident.
- A 30-minute baseline run script demonstrating no false firing.

**Verifies:** G2.3, G2.6. Raise-from-draft path of G3.1.

### M6. Attachments, notifications and on-call

- Attachment types: metric snapshot (frozen), log excerpt, file or screenshot to object storage with server-side size limit and type allowlist, link or note.
- Outbox-driven email through Mailpit on raise, severity change, reassignment to a new team, Resolved and Closed; one email per event to the group address with the on-call in CC. Mail failure never blocks the workflow.
- On-call rotation editor; CC follows the rotation in force.
- Escalation job for unacknowledged incidents, with an escalation record; Admin flag when a team has no on-call.

**Verifies:** G3.1 (complete), G4.1 to G4.7.

### M7. Runbooks and the closure gate

- Runbook form exposed at Resolved with all six mandatory fields; server-side rejection of incomplete submissions.
- Root-cause category restricted to the controlled taxonomy, with free-text detail.
- Review flow: resolver submits, lead or Incident Commander approves or returns with comments; caller's Close enabled only after approval.
- Runbook versioning and search.

**Verifies:** G5.1 to G5.5. Closure becomes possible end to end.

### M8. Live updates and the thin-slice end-to-end test

- WebSocket gateway implementing the behaviour in section 2 (sequence numbers, replay, refetch, bounded queue, heartbeat); a test that drops and restores a connection.
- Playwright test covering the full loop: fault injected, draft created, raised, email visible in Mailpit, teams update, runbook approved, caller closes. Runs in CI against the Compose stack using the drill profile.

**Verifies:** G3.9, G9.3. **Checkpoint:** the thin vertical slice is complete and demonstrable.

### M9. Anomaly detection and dashboards

- Statistical anomaly detection (robust z-score over a rolling median and median absolute deviation, with a minimum run of consecutive anomalous points), feeding the same draft pipeline.
- Prebuilt health dashboard per service (resource usage, request rate, error rate, latency, recent logs, change markers), measured under 2 s with demo data by a script.
- Simple panel builder: add, remove and rearrange metric panels, with the layout persisted per user.

**Verifies:** G2.1, G2.2, G2.4.

### M10. Phase 1 hardening and release

- Permission matrix test confirmed to cover every endpoint and all eight roles; audit coverage confirmed for every listed entity.
- API integration test suite confirmed against real PostgreSQL/TimescaleDB and RustFS containers in CI.
- Clean-machine run-through: one fault injection through the full lifecycle in under 10 minutes; README rewritten from planned to actual behaviour; architecture diagram; ADR set complete.
- Recorded walkthrough. Any figure quoted (for example MTTA in drills) is produced by a script in `scripts/`.

**Verifies:** G8.1, G8.3, G9.1, G9.2, G10.1, G10.2. The walkthrough part of G10.3. The resume-metrics part of G10.3 completes in Phase 2, when accuracy figures exist.

## 5. Check coverage summary

| Milestone | Checks verified |
|---|---|
| M0 | G9.4 |
| M1 | G0.1, G0.2, G0.3 |
| M2 | G1.1, G1.2, G1.3, G1.4, G1.5, G1.6 |
| M3 | G8.2, G8.4 |
| M4 | G3.2, G3.3, G3.4, G3.5, G3.6, G3.7, G3.8, G8.5 |
| M5 | G2.3, G2.6 |
| M6 | G3.1, G4.1, G4.2, G4.3, G4.4, G4.5, G4.6, G4.7 |
| M7 | G5.1, G5.2, G5.3, G5.4, G5.5 |
| M8 | G3.9, G9.3 |
| M9 | G2.1, G2.2, G2.4 |
| M10 | G8.1, G8.3, G9.1, G9.2, G10.1, G10.2, G10.3 (walkthrough) |

All 44 P1 checks are assigned exactly once.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Phase 1 scope is large for a single developer | The thin-slice checkpoint at M8 is a usable, demonstrable product on its own; M9 and M10 can be reordered or paced without invalidating it. |
| Time-dependent behaviour (SLA, escalation, alert duration) makes tests slow or flaky | Pure modules with an injected clock for unit tests; drill profile with short timers for integration and E2E tests. |
| WebSocket reconnect and back-pressure are easy to get subtly wrong | Behaviour fixed in advance (section 2) and covered by a dedicated connection-drop test in M8. |
| Docker Desktop on Windows (the development machine) differs from Linux CI | CI on Linux is the reference; `.gitattributes` prevents line-ending problems in shell scripts and containers. |
| Audit immutability enforced only by convention | Enforced by database grants and a trigger, and verified by a test that attempts an update with the application role. |

## 7. Housekeeping noted during planning

- The README linked to `InfraWatch-2.0-Specification.html`, but the file in the repository was `Great-Observations_Specification.html`. Resolved in M0: the specification now lives at `docs/specification.html` and the link is corrected.

## 8. Progress

| Milestone | State | Notes |
|---|---|---|
| M0 | Implemented | G9.4 is verified once the CI workflow has run on GitHub and the branch ruleset described in `CONTRIBUTING.md` is active. |
| M1 | Implemented | G0.1 to G0.3 are verified by the `compose-smoke` CI job: clean `.env.example` start, every health check green within 120 s, seed run twice with row counts checked. |
| M2 | Implemented | PR 1 (metric ingest, hypertable, agent), PR 2 (demo-app telemetry, log and change-event ingest, fault injection) and PR 3 (charts with change markers at `/telemetry`, log search at `/logs`) verify G1.1 to G1.6 in the `compose-smoke` job through `scripts/check-telemetry.sh`. The chart drawing itself is covered by a unit test of the chart options, not by a browser test; Playwright arrives with G9.3. |
| M3 | Implemented | G8.2 and G8.4 are verified in the `compose-smoke` job by `scripts/check-audit.sh` and `scripts/check-auth.sh`; the permission matrix test covers every route for all eight roles. |
| M4 | In progress | PR 1: incident model, seven-state machine, raise, scoped status updates, caller-only close and reopen, severity changes, status-only view, core coverage floor of 95% in CI. PR 2: parallel team tasks with assignee and checklist, lead-only assignment within the lead's team, Admin-configurable SLA policy, acknowledge and resolve timers derived from status events. Both verified by `scripts/check-incidents.sh`. PR 3 (web pages) follows. |
| M5 to M10 | Not started | |

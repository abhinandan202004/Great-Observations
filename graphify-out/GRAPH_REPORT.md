# Graph Report - Great-Observations  (2026-11-16)

## Corpus Check
- 83 files · ~29,433 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 627 nodes · 912 edges · 66 communities (39 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.89)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `be69dac7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- devDependencies
- Contributing to InfraWatch
- Product Specification Core
- infrawatch_agent/__main__.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- telemetry.py
- Docker Build Inputs
- interval
- services
- CI Docker Matrix
- Workflow Permissions
- compose.yaml
- seed.py
- jobs
- CI Web Job
- scripts
- Incident lifecycle states and transitions (section 6.4)
- test_agent_delivery.py
- steps
- Alerting Milestones
- On-call Notifications
- ServiceNow Integration
- M1 Environment Setup
- M2 Telemetry Ingest
- M7 Runbook Gate
- API-Core Dependency
- Graphify Project Skill
- Ponytail Skill
- Alerting Section
- Open Items
- G6 AI Gate
- G7 ServiceNow Gate
- Glossary
- Risks and Mitigations
- Agent Package
- Demo App Package
- Worker Package
- Workspace Root
- init-infrawatch.sh
- test_ingest_auth.py
- on
- Gate G3 Incident lifecycle (9 checks)
- package.json
- Phase 1 implementation plan
- AI layer design (section 6.7)
- layout.tsx
- infrawatch_api/__main__.py
- Architecture decision records index
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- ADR 0009: WebSockets for real-time updates
- eslint.config.mjs
- InfraWatch web application (Next.js)
- page.test.tsx
- vitest.config.mts
- vitest
- ADR 0016: Continuous integration and container builds
- ci-passed
- check-telemetry.sh

## God Nodes (most connected - your core abstractions)
1. `InfraWatch 2.0 README overview` - 20 edges
2. `Architecture decision records index` - 20 edges
3. `Sample` - 18 edges
4. `Buffer` - 17 edges
5. `with` - 17 edges
6. `compilerOptions` - 16 edges
7. `test_readings_continue_while_delivery_is_stuck()` - 12 edges
8. `flush()` - 11 edges
9. `Phase 1 implementation plan` - 11 edges
10. `deliver_forever()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `AI layer two-tier design` --semantically_similar_to--> `AI layer design (section 6.7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Compose architecture and principal data entities` --semantically_similar_to--> `Compose architecture and principal data entities (section 7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Full agreed decision register` --semantically_similar_to--> `Specification decision register`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Incident lifecycle and transitions` --semantically_similar_to--> `Incident lifecycle states and transitions (section 6.4)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Role/capability permission matrix` --semantically_similar_to--> `Eight roles and permission matrix`  [INFERRED] [semantically similar]
  context.md → docs/specification.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **InfraWatch authentication credential stack** — docs_adr_0011_argon2id, docs_adr_0011_access_jwt, docs_adr_0011_refresh_token, docs_adr_0011_per_agent_api_key, docs_adr_0011_hmac_sha256 [EXTRACTED 1.00]
- **GitHub Actions CI job set** — docs_adr_0016_github_actions_workflow, docs_adr_0016_ci_passed_job, docs_adr_0016_python_dockerfile, docs_adr_0016_gitleaks_scan, docs_adr_0016_branch_protection [EXTRACTED 1.00]
- **Broker-free PostgreSQL-centric infrastructure (queue + outbox + fan-out)** — docs_adr_0008_outbox_table, docs_adr_0008_select_for_update_skip_locked, docs_adr_0010_listen_notify, docs_adr_0010_incident_event_log [EXTRACTED 1.00]
- **Server-side enforcement, degrade gracefully, configuration over code, reproducibility** — readme_architecture, context_design_principles, docs_specification_architecture [INFERRED 0.85]
- **Four-stage flow across all specification documents** — readme_four_stage_flow, context_four_stage_flow, docs_specification_overview [INFERRED 0.85]
- **Three-phase delivery roadmap P1/P2/P3** — readme_roadmap, context_phasing, docs_specification_phasing, docs_phase_1_plan_scope [INFERRED 0.85]

## Communities (66 total, 27 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+7 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.25
Nodes (9): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Working practices (branches, commits, server-side enforcement), M0 Repository foundation and CI, M10 Phase 1 hardening and release, Gate G10 The demonstration (3 checks) (+1 more)

### Community 2 - "Product Specification Core"
Cohesion: 0.09
Nodes (23): Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks, Compose architecture and principal data entities (section 7), Business case (problem, value, portfolio) (+15 more)

### Community 3 - "infrawatch_agent/__main__.py"
Cohesion: 0.07
Nodes (13): backoff_delay(), HealthHandler, main(), stop_process(), test_backoff_stays_between_one_and_sixty_seconds(), base_url(), test_health_reports_ok(), test_unknown_path_is_not_found() (+5 more)

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "telemetry.py"
Cohesion: 0.07
Nodes (16): post(), create_app(), health(), HealthResponse, lifespan(), ingest_metrics(), IngestResult, metric_series() (+8 more)

### Community 7 - "Docker Build Inputs"
Cohesion: 0.14
Nodes (14): with, build-args, cache, cache-dependency-path, cache-from, cache-to, context, enable-cache (+6 more)

### Community 8 - "interval"
Cohesion: 0.12
Nodes (34): healthcheck, healthcheck, environment, healthcheck, image, volumes, healthcheck, DB_APP_PASSWORD (+26 more)

### Community 9 - "services"
Cohesion: 0.06
Nodes (45): build, environment, image, volumes, build, depends_on, environment, image (+37 more)

### Community 10 - "CI Docker Matrix"
Cohesion: 0.18
Nodes (11): name, runs-on, steps, strategy, build-args, file, service, docker (+3 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.17
Nodes (12): GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, secrets, permissions, contents, pull-requests, name (+4 more)

### Community 12 - "compose.yaml"
Cohesion: 0.12
Nodes (15): name, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context, dockerfile (+7 more)

### Community 13 - "seed.py"
Cohesion: 0.08
Nodes (9): main(), run_migrations(), upgrade(), DemoService, DemoUser, main(), seed(), test_every_role_has_exactly_one_demo_user() (+1 more)

### Community 14 - "jobs"
Cohesion: 0.22
Nodes (8): name, runs-on, concurrency, cancel-in-progress, group, jobs, compose-smoke, name

### Community 15 - "CI Web Job"
Cohesion: 0.33
Nodes (6): run, web, working-directory, defaults, name, runs-on

### Community 16 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:coverage, typecheck

### Community 17 - "Incident lifecycle states and transitions (section 6.4)"
Cohesion: 0.22
Nodes (8): Incident lifecycle and transitions, Runbook process and controlled taxonomy, Controlled root cause taxonomy (seven categories), Incident lifecycle states and transitions (section 6.4), Runbook form fields and process (section 6.6), Seven-state incident lifecycle, Structured runbook mandatory fields, Severity and SLA defaults (P1-P4)

### Community 18 - "test_agent_delivery.py"
Cohesion: 0.09
Nodes (20): Buffer, Sample, Collector, collect_forever(), deliver_forever(), flush(), CountingCollector, samples() (+12 more)

### Community 19 - "steps"
Cohesion: 0.27
Nodes (11): steps, steps, python, name, runs-on, steps, if, name (+3 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 43 - "test_ingest_auth.py"
Cohesion: 0.10
Nodes (4): client(), test_ingest_rejects_everything_when_no_keys_are_configured(), test_ingest_rejects_missing_or_wrong_key(), test_ingest_rejects_naive_timestamps_and_nan()

### Community 44 - "on"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 45 - "Gate G3 Incident lifecycle (9 checks)"
Cohesion: 0.17
Nodes (12): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Python collector agent SQLite buffer and retry policy, Decisions confirmed on 2026-11-09, M3 Identity, RBAC and audit foundation, M4 Incident lifecycle core, M6 Attachments, notifications and on-call, M8 Live updates and thin-slice end-to-end test, WebSocket sequence numbers, replay and back-pressure policy (+4 more)

### Community 46 - "package.json"
Cohesion: 0.22
Nodes (10): dependencies, react@19.3.0, react-dom@19.3.0, engines, node, name, private, version (+2 more)

### Community 47 - "Phase 1 implementation plan"
Cohesion: 0.27
Nodes (10): infrawatch-api FastAPI service, infrawatch-demo-app, infrawatch-worker package, WebSocket gateway, Permission policy in infrawatch-core, Transactional audit entry (actor, action, before/after), Shared python.Dockerfile, Phase 1 implementation plan (+2 more)

### Community 48 - "AI layer design (section 6.7)"
Cohesion: 0.50
Nodes (3): AI layer two-tier design, AI layer design (section 6.7), AI layer (retrieval + reasoning)

### Community 50 - "layout.tsx"
Cohesion: 0.25
Nodes (4): nextConfig, next@16.4.5, metadata, next

### Community 53 - "Architecture decision records index"
Cohesion: 0.13
Nodes (15): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, 0017. Object storage with RustFS, Consequences, Context (+7 more)

### Community 54 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.28
Nodes (8): Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, PostgreSQL LISTEN/NOTIFY channel, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation, ADR 0013: Standalone ticketing with optional ServiceNow sync

### Community 55 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.40
Nodes (6): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log

### Community 56 - "eslint.config.mjs"
Cohesion: 0.33
Nodes (5): eslintConfig, eslint@^9.39.5, eslint-config-next@16.4.5, eslint, eslint-config-next

### Community 57 - "InfraWatch web application (Next.js)"
Cohesion: 0.40
Nodes (5): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout

### Community 58 - "page.test.tsx"
Cohesion: 0.50
Nodes (3): @testing-library/react@^16.3.3, HomePage(), @testing-library/react

### Community 59 - "vitest.config.mts"
Cohesion: 0.40
Nodes (4): vite-tsconfig-paths@^6.1.1, @vitejs/plugin-react@^6.2.1, vite-tsconfig-paths, @vitejs/plugin-react

### Community 60 - "vitest"
Cohesion: 0.50
Nodes (3): vitest@^5.1.0, GET(), vitest

### Community 61 - "ADR 0016: Continuous integration and container builds"
Cohesion: 0.50
Nodes (5): Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan

### Community 62 - "ci-passed"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, ci-passed

### Community 63 - "check-telemetry.sh"
Cohesion: 0.60
Nodes (4): check-telemetry.sh script, sql(), utc_now(), wait_for_points_since()

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-api`, `infrawatch-core`, `infrawatch-agent`, `infrawatch-demo-app`, `infrawatch-worker` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 271 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture decision records index` connect `Architecture decision records index` to `Contributing to InfraWatch`, `Product Specification Core`, `ADR 0011: Authentication and tokens`, `ADR 0008: Job queue and transactional outbox in PostgreSQL`, `ADR 0009: WebSockets for real-time updates`, `InfraWatch web application (Next.js)`, `ADR 0016: Continuous integration and container builds`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Sample` (e.g. with `Collector` and `CountingCollector`) actually correct?**
  _`Sample` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-api`, `infrawatch-core`, `infrawatch-agent` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Contributing to InfraWatch`, `Phase 1 implementation plan`, `AI layer design (section 6.7)`, `Incident lifecycle states and transitions (section 6.4)`, `Architecture decision records index`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Buffer` (e.g. with `test_buffer_drops_oldest_when_full_and_reports_count()` and `test_buffer_survives_reopen()`) actually correct?**
  _`Buffer` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Product Specification Core` be split into smaller, more focused modules?**
  _Cohesion score 0.08923076923076922 - nodes in this community are weakly interconnected._
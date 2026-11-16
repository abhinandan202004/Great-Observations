# Graph Report - Great-Observations  (2026-11-17)

## Corpus Check
- 88 files · ~32,622 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 705 nodes · 1120 edges · 73 communities (44 shown, 29 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.89)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `6cf4b304`
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
- args
- CI Docker Matrix
- Workflow Permissions
- compose.yaml
- seed.py
- jobs
- CI Web Job
- scripts
- infrawatch_demo_app/main.py
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
- on
- Gate G3 Incident lifecycle (9 checks)
- package.json
- Phase 1 implementation plan
- collections_abc
- layout.tsx
- migrate
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
- environment
- services
- demo-app
- ADR 0006 PostgreSQL with TimescaleDB and pgvector
- environment
- healthcheck

## God Nodes (most connected - your core abstractions)
1. `InfraWatch 2.0 README overview` - 20 edges
2. `Architecture decision records index` - 20 edges
3. `Sample` - 18 edges
4. `with` - 17 edges
5. `Buffer` - 17 edges
6. `compilerOptions` - 16 edges
7. `test_readings_continue_while_delivery_is_stuck()` - 12 edges
8. `flush()` - 11 edges
9. `Phase 1 implementation plan` - 11 edges
10. `create_app()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Incident lifecycle and transitions` --semantically_similar_to--> `Incident lifecycle states and transitions (section 6.4)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Runbook process and controlled taxonomy` --semantically_similar_to--> `Runbook form fields and process (section 6.6)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Severity and SLA defaults (P1-P4)` --semantically_similar_to--> `Incident lifecycle states and transitions (section 6.4)`  [INFERRED] [semantically similar]
  README.md → docs/specification.html
- `Compose architecture and principal data entities` --semantically_similar_to--> `Compose architecture and principal data entities (section 7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Full agreed decision register` --semantically_similar_to--> `Specification decision register`  [INFERRED] [semantically similar]
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

## Communities (73 total, 29 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+7 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.19
Nodes (12): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Web CI checks (npm lint, typecheck, test), Working practices (branches, commits, server-side enforcement), M0 Repository foundation and CI, M10 Phase 1 hardening and release (+4 more)

### Community 2 - "Product Specification Core"
Cohesion: 0.06
Nodes (34): AI layer two-tier design, Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, Incident lifecycle and transitions, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks (+26 more)

### Community 3 - "infrawatch_agent/__main__.py"
Cohesion: 0.07
Nodes (20): HealthHandler, base_url(), test_health_reports_ok(), test_unknown_path_is_not_found(), client(), signed(), test_change_webhook_rejects_a_bad_signature(), test_change_webhook_rejects_a_body_changed_after_signing() (+12 more)

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "telemetry.py"
Cohesion: 0.07
Nodes (20): post(), create_app(), health(), HealthResponse, lifespan(), main(), run_migrations(), ChangeEvent (+12 more)

### Community 7 - "Docker Build Inputs"
Cohesion: 0.14
Nodes (14): with, build-args, cache, cache-dependency-path, cache-from, cache-to, context, enable-cache (+6 more)

### Community 8 - "interval"
Cohesion: 0.22
Nodes (22): healthcheck, healthcheck, image, volumes, healthcheck, interval, retries, start_interval (+14 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

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
Cohesion: 0.15
Nodes (6): DemoService, DemoUser, main(), seed(), test_every_role_has_exactly_one_demo_user(), Role

### Community 14 - "jobs"
Cohesion: 0.22
Nodes (8): name, runs-on, concurrency, cancel-in-progress, group, jobs, compose-smoke, name

### Community 15 - "CI Web Job"
Cohesion: 0.33
Nodes (6): run, web, working-directory, defaults, name, runs-on

### Community 16 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:coverage, typecheck

### Community 17 - "infrawatch_demo_app/main.py"
Cohesion: 0.06
Nodes (28): StopReadingsError, FaultActiveError, Faults, checkout(), CheckoutResponse, create_app(), health(), post_checkout() (+20 more)

### Community 18 - "test_agent_delivery.py"
Cohesion: 0.08
Nodes (23): Buffer, Sample, Collector, backoff_delay(), collect_forever(), deliver_forever(), flush(), main() (+15 more)

### Community 19 - "steps"
Cohesion: 0.27
Nodes (11): steps, steps, python, name, runs-on, steps, if, name (+3 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 44 - "on"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 45 - "Gate G3 Incident lifecycle (9 checks)"
Cohesion: 0.25
Nodes (8): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Decisions confirmed on 2026-11-09, M4 Incident lifecycle core, M6 Attachments, notifications and on-call, M8 Live updates and thin-slice end-to-end test, WebSocket sequence numbers, replay and back-pressure policy, Gate G3 Incident lifecycle (9 checks), Gate G4 Attachments, notifications and on-call (7 checks)

### Community 46 - "package.json"
Cohesion: 0.22
Nodes (10): dependencies, react@19.3.0, react-dom@19.3.0, engines, node, name, private, version (+2 more)

### Community 47 - "Phase 1 implementation plan"
Cohesion: 0.24
Nodes (10): infrawatch-api FastAPI service, infrawatch-demo-app, infrawatch-worker package, WebSocket gateway, PostgreSQL LISTEN/NOTIFY channel, Permission policy in infrawatch-core, Shared python.Dockerfile, Phase 1 implementation plan (+2 more)

### Community 50 - "layout.tsx"
Cohesion: 0.25
Nodes (4): nextConfig, next@16.4.5, metadata, next

### Community 51 - "migrate"
Cohesion: 0.17
Nodes (12): environment, condition, db, CHANGE_WEBHOOK_SECRET, DATABASE_URL, INGEST_API_KEYS, command, depends_on (+4 more)

### Community 53 - "Architecture decision records index"
Cohesion: 0.19
Nodes (11): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, Architecture decision records index, ADR template (Context, Decision, Consequences), Proposed technical foundations (toolchain, persistence, queue, auth, audit) (+3 more)

### Community 54 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.33
Nodes (7): Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation, ADR 0013: Standalone ticketing with optional ServiceNow sync

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
Cohesion: 0.39
Nodes (6): fault(), check-telemetry.sh script, sql(), utc_now(), wait_for_points_since(), wait_until()

### Community 64 - "environment"
Cohesion: 0.20
Nodes (10): RUSTFS_ACCESS_KEY, RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, RUSTFS_SECRET_KEY, environment, image, ports (+2 more)

### Community 65 - "services"
Cohesion: 0.22
Nodes (9): depends_on, image, ports, migrate, condition, services, api, worker (+1 more)

### Community 68 - "demo-app"
Cohesion: 0.29
Nodes (8): environment, environment, image, ports, AGENT_SERVICE, INGEST_API_KEY, INGEST_URL, demo-app

### Community 69 - "ADR 0006 PostgreSQL with TimescaleDB and pgvector"
Cohesion: 0.25
Nodes (6): 0017. Object storage with RustFS, Consequences, Context, Decision, Python collector agent SQLite buffer and retry policy, Telemetry collection and storage (section 6.1)

### Community 70 - "environment"
Cohesion: 0.40
Nodes (5): environment, DB_APP_PASSWORD, DB_OWNER_PASSWORD, POSTGRES_INITDB_ARGS, POSTGRES_PASSWORD

### Community 71 - "healthcheck"
Cohesion: 0.50
Nodes (4): healthcheck, image, volumes, agent

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-demo-app`, `infrawatch-api`, `infrawatch-core`, `infrawatch-agent`, `infrawatch-worker` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 286 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture decision records index` connect `Architecture decision records index` to `Contributing to InfraWatch`, `Product Specification Core`, `ADR 0011: Authentication and tokens`, `ADR 0006 PostgreSQL with TimescaleDB and pgvector`, `ADR 0008: Job queue and transactional outbox in PostgreSQL`, `ADR 0009: WebSockets for real-time updates`, `InfraWatch web application (Next.js)`, `ADR 0016: Continuous integration and container builds`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Sample` (e.g. with `Collector` and `CountingCollector`) actually correct?**
  _`Sample` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-demo-app`, `infrawatch-api`, `infrawatch-core` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Contributing to InfraWatch`, `Architecture decision records index`, `Phase 1 implementation plan`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Buffer` (e.g. with `test_buffer_drops_oldest_when_full_and_reports_count()` and `test_buffer_survives_reopen()`) actually correct?**
  _`Buffer` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Product Specification Core` be split into smaller, more focused modules?**
  _Cohesion score 0.059379217273954114 - nodes in this community are weakly interconnected._
# Graph Report - Great-Observations  (2026-11-16)

## Corpus Check
- 83 files · ~29,405 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 620 nodes · 895 edges · 68 communities (42 shown, 26 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.9)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `eea49277`
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
- services
- args
- CI Docker Matrix
- Workflow Permissions
- compose.yaml
- seed.py
- ci.yml
- CI Web Job
- scripts
- environment
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
- ADR 0006 PostgreSQL with TimescaleDB and pgvector
- Gate G3 Incident lifecycle (9 checks)
- package.json
- Phase 1 implementation plan
- api
- migrate
- layout.tsx
- agent
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
- healthcheck

## God Nodes (most connected - your core abstractions)
1. `InfraWatch 2.0 README overview` - 20 edges
2. `Architecture decision records index` - 20 edges
3. `Sample` - 19 edges
4. `Buffer` - 17 edges
5. `with` - 17 edges
6. `compilerOptions` - 16 edges
7. `test_readings_continue_while_delivery_is_stuck()` - 12 edges
8. `flush()` - 11 edges
9. `main()` - 11 edges
10. `Phase 1 implementation plan` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Compose architecture and principal data entities` --semantically_similar_to--> `Compose architecture and principal data entities (section 7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Full agreed decision register` --semantically_similar_to--> `Specification decision register`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Incident lifecycle and transitions` --semantically_similar_to--> `Incident lifecycle states and transitions (section 6.4)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Role/capability permission matrix` --semantically_similar_to--> `Eight roles and permission matrix`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Phasing P1/P2/P3 and acceptance checks` --semantically_similar_to--> `Phasing P1/P2/P3 (section 9)`  [INFERRED] [semantically similar]
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

## Communities (68 total, 26 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+7 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.33
Nodes (6): Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Web CI checks (npm lint, typecheck, test), Working practices (branches, commits, server-side enforcement), Gate G10 The demonstration (3 checks)

### Community 2 - "Product Specification Core"
Cohesion: 0.06
Nodes (33): AI layer two-tier design, Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, Incident lifecycle and transitions, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks (+25 more)

### Community 3 - "infrawatch_agent/__main__.py"
Cohesion: 0.08
Nodes (13): backoff_delay(), HealthHandler, main(), stop_process(), test_backoff_stays_between_one_and_sixty_seconds(), base_url(), test_health_reports_ok(), test_unknown_path_is_not_found() (+5 more)

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.17
Nodes (12): Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Permission policy in infrawatch-core, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter), httpx delivery client (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "telemetry.py"
Cohesion: 0.07
Nodes (16): post(), create_app(), health(), HealthResponse, lifespan(), ingest_metrics(), IngestResult, metric_series() (+8 more)

### Community 7 - "Docker Build Inputs"
Cohesion: 0.14
Nodes (14): with, build-args, cache, cache-dependency-path, cache-from, cache-to, context, enable-cache (+6 more)

### Community 8 - "services"
Cohesion: 0.17
Nodes (22): healthcheck, healthcheck, healthcheck, image, ports, interval, retries, test (+14 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

### Community 10 - "CI Docker Matrix"
Cohesion: 0.18
Nodes (11): name, runs-on, steps, strategy, build-args, file, service, docker (+3 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.25
Nodes (8): GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, secrets, name, runs-on, steps, env

### Community 12 - "compose.yaml"
Cohesion: 0.13
Nodes (14): name, services, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context (+6 more)

### Community 13 - "seed.py"
Cohesion: 0.07
Nodes (9): main(), run_migrations(), upgrade(), DemoService, DemoUser, main(), seed(), test_every_role_has_exactly_one_demo_user() (+1 more)

### Community 14 - "ci.yml"
Cohesion: 0.14
Nodes (13): concurrency, cancel-in-progress, group, name, on, pull_request, push, permissions (+5 more)

### Community 15 - "CI Web Job"
Cohesion: 0.33
Nodes (6): run, web, working-directory, defaults, name, runs-on

### Community 16 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:coverage, typecheck

### Community 17 - "environment"
Cohesion: 0.20
Nodes (10): RUSTFS_ACCESS_KEY, RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, RUSTFS_SECRET_KEY, environment, image, ports (+2 more)

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

### Community 44 - "ADR 0006 PostgreSQL with TimescaleDB and pgvector"
Cohesion: 0.18
Nodes (9): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), 0017. Object storage with RustFS, Consequences, Context, Decision, Python collector agent SQLite buffer and retry policy, Decisions confirmed on 2026-11-09, WebSocket sequence numbers, replay and back-pressure policy (+1 more)

### Community 45 - "Gate G3 Incident lifecycle (9 checks)"
Cohesion: 0.20
Nodes (11): Protect main branch ruleset (ci-passed check), M0 Repository foundation and CI, M10 Phase 1 hardening and release, M3 Identity, RBAC and audit foundation, M4 Incident lifecycle core, M6 Attachments, notifications and on-call, M8 Live updates and thin-slice end-to-end test, Gate G3 Incident lifecycle (9 checks) (+3 more)

### Community 46 - "package.json"
Cohesion: 0.22
Nodes (10): dependencies, react@19.3.0, react-dom@19.3.0, engines, node, name, private, version (+2 more)

### Community 47 - "Phase 1 implementation plan"
Cohesion: 0.32
Nodes (8): infrawatch-agent package, infrawatch-api FastAPI service, infrawatch-demo-app, WebSocket gateway, Per-agent API key, Shared python.Dockerfile, Phase 1 implementation plan, Phase 1 scope (44 P1 checks plus G10.1/G10.2/walkthrough)

### Community 48 - "api"
Cohesion: 0.20
Nodes (10): depends_on, environment, image, ports, migrate, DATABASE_URL, INGEST_API_KEYS, condition (+2 more)

### Community 49 - "migrate"
Cohesion: 0.29
Nodes (7): condition, db, command, depends_on, image, restart, migrate

### Community 50 - "layout.tsx"
Cohesion: 0.25
Nodes (4): nextConfig, next@16.4.5, metadata, next

### Community 51 - "agent"
Cohesion: 0.29
Nodes (7): environment, image, volumes, AGENT_SERVICE, INGEST_API_KEY, INGEST_URL, agent

### Community 53 - "Architecture decision records index"
Cohesion: 0.16
Nodes (12): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, Architecture decision records index, ADR template (Context, Decision, Consequences), Proposed technical foundations (toolchain, persistence, queue, auth, audit) (+4 more)

### Community 54 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.24
Nodes (9): infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, PostgreSQL LISTEN/NOTIFY channel, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation (+1 more)

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
Cohesion: 0.22
Nodes (9): if, name, needs, runs-on, name, runs-on, jobs, ci-passed (+1 more)

### Community 63 - "check-telemetry.sh"
Cohesion: 0.60
Nodes (4): check-telemetry.sh script, sql(), utc_now(), wait_for_points_since()

### Community 64 - "healthcheck"
Cohesion: 0.25
Nodes (8): environment, healthcheck, image, volumes, DB_APP_PASSWORD, DB_OWNER_PASSWORD, POSTGRES_PASSWORD, db

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-api`, `infrawatch-core`, `infrawatch-agent`, `infrawatch-demo-app`, `infrawatch-worker` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 266 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture decision records index` connect `Architecture decision records index` to `Contributing to InfraWatch`, `Product Specification Core`, `ADR 0011: Authentication and tokens`, `ADR 0006 PostgreSQL with TimescaleDB and pgvector`, `ADR 0008: Job queue and transactional outbox in PostgreSQL`, `ADR 0009: WebSockets for real-time updates`, `InfraWatch web application (Next.js)`, `ADR 0016: Continuous integration and container builds`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Sample` (e.g. with `Collector` and `deliver_forever()`) actually correct?**
  _`Sample` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-api`, `infrawatch-core`, `infrawatch-agent` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Contributing to InfraWatch`, `Architecture decision records index`, `Phase 1 implementation plan`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Buffer` (e.g. with `collect_forever()` and `flush()`) actually correct?**
  _`Buffer` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `Product Specification Core` be split into smaller, more focused modules?**
  _Cohesion score 0.06156156156156156 - nodes in this community are weakly interconnected._
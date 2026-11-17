# Graph Report - Great-Observations  (2026-11-17)

## Corpus Check
- 91 files · ~34,259 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 723 nodes · 1177 edges · 67 communities (44 shown, 23 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.89)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `dcada69a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- devDependencies
- Contributing to InfraWatch
- Product Specification Core
- test_agent_entrypoint.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- telemetry.py
- with
- interval
- args
- telemetry/page.tsx
- Workflow Permissions
- compose.yaml
- infrawatch_api/main.py
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
- compose-smoke
- package.json
- infrawatch-api FastAPI service
- layout.tsx
- migrate
- Architecture decision records index
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- ADR 0009: WebSockets for real-time updates
- eslint.config.mjs
- InfraWatch web application (Next.js)
- page.test.tsx
- vitest.config.mts
- vitest
- ci-passed
- check-telemetry.sh
- environment
- services
- demo-app
- ADR 0006 PostgreSQL with TimescaleDB and pgvector
- environment
- healthcheck
- test_ingest_auth.py

## God Nodes (most connected - your core abstractions)
1. `InfraWatch 2.0 README overview` - 20 edges
2. `Architecture decision records index` - 20 edges
3. `Sample` - 19 edges
4. `Buffer` - 17 edges
5. `compilerOptions` - 16 edges
6. `test_readings_continue_while_delivery_is_stuck()` - 12 edges
7. `flush()` - 11 edges
8. `main()` - 11 edges
9. `search_logs()` - 11 edges
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

## Communities (67 total, 23 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+7 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.13
Nodes (17): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Web CI checks (npm lint, typecheck, test), Working practices (branches, commits, server-side enforcement), M0 Repository foundation and CI, M10 Phase 1 hardening and release (+9 more)

### Community 2 - "Product Specification Core"
Cohesion: 0.06
Nodes (34): AI layer two-tier design, Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, Incident lifecycle and transitions, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks (+26 more)

### Community 3 - "test_agent_entrypoint.py"
Cohesion: 0.06
Nodes (9): test_health_reports_ok(), test_unknown_path_is_not_found(), upgrade(), main(), HealthHandler, main(), base_url(), test_health_reports_ok() (+1 more)

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "telemetry.py"
Cohesion: 0.09
Nodes (20): post(), change_markers(), ChangeEvent, ChangeMarker, ingest_change(), ingest_logs(), ingest_metrics(), IngestResult (+12 more)

### Community 7 - "with"
Cohesion: 0.29
Nodes (7): with, cache, cache-dependency-path, enable-cache, fetch-depth, node-version, version

### Community 8 - "interval"
Cohesion: 0.22
Nodes (22): healthcheck, healthcheck, image, volumes, healthcheck, interval, retries, start_interval (+14 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

### Community 10 - "telemetry/page.tsx"
Cohesion: 0.27
Nodes (10): react@19.3.0, Change, Chart(), chartOption(), Point, TelemetryPage(), load(), formatTime() (+2 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.12
Nodes (15): name, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context, dockerfile (+7 more)

### Community 13 - "infrawatch_api/main.py"
Cohesion: 0.05
Nodes (16): stop_process(), create_app(), health(), HealthResponse, lifespan(), main(), _NoHealthFilter, main() (+8 more)

### Community 14 - "jobs"
Cohesion: 0.22
Nodes (8): concurrency, cancel-in-progress, group, jobs, python, name, name, runs-on

### Community 15 - "CI Web Job"
Cohesion: 0.29
Nodes (7): run, web, working-directory, defaults, name, runs-on, steps

### Community 16 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:coverage, typecheck

### Community 17 - "infrawatch_demo_app/main.py"
Cohesion: 0.09
Nodes (20): FaultActiveError, Faults, checkout(), CheckoutResponse, create_app(), health(), post_checkout(), start_fault() (+12 more)

### Community 18 - "test_agent_delivery.py"
Cohesion: 0.07
Nodes (25): Buffer, Sample, Collector, backoff_delay(), collect_forever(), deliver_forever(), flush(), HealthHandler (+17 more)

### Community 19 - "steps"
Cohesion: 0.23
Nodes (12): steps, steps, GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, steps, steps, env (+4 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 44 - "on"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 45 - "compose-smoke"
Cohesion: 0.67
Nodes (3): name, runs-on, compose-smoke

### Community 46 - "package.json"
Cohesion: 0.20
Nodes (11): dependencies, echarts@^6.1.0, next@16.4.5, react-dom@19.3.0, engines, node, name, private (+3 more)

### Community 47 - "infrawatch-api FastAPI service"
Cohesion: 0.24
Nodes (10): infrawatch-api FastAPI service, infrawatch-demo-app, Permission policy in infrawatch-core, Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan (+2 more)

### Community 50 - "layout.tsx"
Cohesion: 0.29
Nodes (3): nextConfig, metadata, next

### Community 51 - "migrate"
Cohesion: 0.17
Nodes (12): environment, condition, db, CHANGE_WEBHOOK_SECRET, DATABASE_URL, INGEST_API_KEYS, command, depends_on (+4 more)

### Community 53 - "Architecture decision records index"
Cohesion: 0.19
Nodes (11): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, Architecture decision records index, ADR template (Context, Decision, Consequences), Proposed technical foundations (toolchain, persistence, queue, auth, audit) (+3 more)

### Community 54 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.24
Nodes (9): infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, PostgreSQL LISTEN/NOTIFY channel, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation (+1 more)

### Community 55 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.33
Nodes (7): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, WebSocket gateway, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log

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

### Community 62 - "ci-passed"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, ci-passed

### Community 63 - "check-telemetry.sh"
Cohesion: 0.31
Nodes (7): api(), fault(), check-telemetry.sh script, sql(), utc_now(), wait_for_points_since(), wait_until()

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
Cohesion: 0.17
Nodes (11): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), 0017. Object storage with RustFS, Consequences, Context, Decision, Python collector agent SQLite buffer and retry policy, Decisions confirmed on 2026-11-09, Phase 1 implementation plan (+3 more)

### Community 70 - "environment"
Cohesion: 0.40
Nodes (5): environment, DB_APP_PASSWORD, DB_OWNER_PASSWORD, POSTGRES_INITDB_ARGS, POSTGRES_PASSWORD

### Community 71 - "healthcheck"
Cohesion: 0.50
Nodes (4): healthcheck, image, volumes, agent

### Community 72 - "test_ingest_auth.py"
Cohesion: 0.09
Nodes (19): client(), signed(), test_change_webhook_rejects_a_bad_signature(), test_change_webhook_rejects_a_body_changed_after_signing(), test_change_webhook_rejects_everything_when_no_secret_is_configured(), test_change_webhook_validates_a_correctly_signed_body(), test_ingest_rejects_everything_when_no_keys_are_configured(), test_ingest_rejects_missing_or_wrong_key() (+11 more)

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app`, `infrawatch-worker`, `infrawatch-core` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture decision records index` connect `Architecture decision records index` to `Contributing to InfraWatch`, `Product Specification Core`, `ADR 0011: Authentication and tokens`, `ADR 0006 PostgreSQL with TimescaleDB and pgvector`, `infrawatch-api FastAPI service`, `ADR 0008: Job queue and transactional outbox in PostgreSQL`, `ADR 0009: WebSockets for real-time updates`, `InfraWatch web application (Next.js)`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Sample` (e.g. with `Collector` and `deliver_forever()`) actually correct?**
  _`Sample` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Contributing to InfraWatch`, `ADR 0006 PostgreSQL with TimescaleDB and pgvector`, `Architecture decision records index`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Buffer` (e.g. with `collect_forever()` and `flush()`) actually correct?**
  _`Buffer` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `Contributing to InfraWatch` be split into smaller, more focused modules?**
  _Cohesion score 0.13450292397660818 - nodes in this community are weakly interconnected._
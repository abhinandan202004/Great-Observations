# Graph Report - Great-Observations  (2026-11-18)

## Corpus Check
- 115 files · ~41,938 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 935 nodes · 1729 edges · 94 communities (56 shown, 38 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 150 edges (avg confidence: 0.91)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `eb6504b7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- devDependencies
- Contributing to InfraWatch
- InfraWatch 2.0 README overview
- test_agent_entrypoint.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- auth.py
- with
- interval
- args
- telemetry/page.tsx
- Workflow Permissions
- compose.yaml
- infrawatch_api/__main__.py
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
- infrawatch_api/telemetry.py
- on
- compose-smoke
- incidents.py
- collections_abc
- Incident lifecycle states and transitions (section 6.4)
- Sample
- layout.tsx
- migrate
- logs/page.tsx
- Architecture decision records index
- AI layer design (section 6.7)
- backoff_delay
- api.ts
- InfraWatch web application (Next.js)
- vitest
- check-audit.sh
- faults.py
- threading
- ci-passed
- check-telemetry.sh
- environment
- depends_on
- Reporter
- test_permission_matrix.py
- healthcheck
- Gate G3 Incident lifecycle (9 checks)
- environment
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- test_ingest_auth.py
- infrawatch-api FastAPI service
- infrawatch_demo_app/telemetry.py
- ADR 0009: WebSockets for real-time updates
- Buffer
- check-incidents.sh
- check-auth.sh
- env.py
- environment
- login/page.tsx

## God Nodes (most connected - your core abstractions)
1. `Capability` - 27 edges
2. `InfraWatch 2.0 README overview` - 20 edges
3. `Architecture decision records index` - 20 edges
4. `Sample` - 19 edges
5. `change_status()` - 18 edges
6. `Buffer` - 17 edges
7. `record()` - 17 edges
8. `compilerOptions` - 16 edges
9. `post()` - 15 edges
10. `get_incident()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Compose architecture and principal data entities` --semantically_similar_to--> `Compose architecture and principal data entities (section 7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Full agreed decision register` --semantically_similar_to--> `Specification decision register`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Role/capability permission matrix` --semantically_similar_to--> `Eight roles and permission matrix`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Phasing P1/P2/P3 and acceptance checks` --semantically_similar_to--> `Phasing P1/P2/P3 (section 9)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Market positioning and differentiators` --semantically_similar_to--> `Business case (problem, value, portfolio)`  [INFERRED] [semantically similar]
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

## Communities (94 total, 38 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.09
Nodes (29): eslintConfig, devDependencies, eslint@^9.39.5, eslint-config-next@16.4.5, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19 (+21 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.21
Nodes (11): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Working practices (branches, commits, server-side enforcement), Permission policy in infrawatch-core, M0 Repository foundation and CI, M10 Phase 1 hardening and release (+3 more)

### Community 2 - "InfraWatch 2.0 README overview"
Cohesion: 0.09
Nodes (23): Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks, Compose architecture and principal data entities (section 7), Business case (problem, value, portfolio) (+15 more)

### Community 3 - "test_agent_entrypoint.py"
Cohesion: 0.16
Nodes (7): main(), test_health_reports_ok(), test_unknown_path_is_not_found(), main(), main(), test_health_reports_ok(), test_unknown_path_is_not_found()

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "auth.py"
Cohesion: 0.06
Nodes (35): post(), AccessRequestIn, ApprovalIn, approve_request(), create_user(), _create_user(), pending_requests(), reject_request() (+27 more)

### Community 7 - "with"
Cohesion: 0.29
Nodes (7): with, cache, cache-dependency-path, enable-cache, fetch-depth, node-version, version

### Community 8 - "interval"
Cohesion: 0.22
Nodes (22): healthcheck, healthcheck, image, volumes, healthcheck, image, ports, interval (+14 more)

### Community 9 - "args"
Cohesion: 0.19
Nodes (17): build, build, image, ports, MODULE, PACKAGE, args, context (+9 more)

### Community 10 - "telemetry/page.tsx"
Cohesion: 0.38
Nodes (7): Change, Chart(), chartOption(), Point, TelemetryPage(), formatTime(), react

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.12
Nodes (15): name, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context, dockerfile (+7 more)

### Community 13 - "infrawatch_api/__main__.py"
Cohesion: 0.22
Nodes (3): main(), _NoHealthFilter, main()

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
Cohesion: 0.19
Nodes (13): checkout(), CheckoutResponse, create_app(), health(), post_checkout(), start_fault(), stop_fault(), FaultResponse (+5 more)

### Community 18 - "test_agent_delivery.py"
Cohesion: 0.18
Nodes (13): CountingCollector, samples(), status_error(), StopReadingsError, test_buffer_drops_oldest_when_full_and_reports_count(), test_buffer_survives_reopen(), test_flush_drops_a_batch_the_api_rejects_as_malformed(), malformed() (+5 more)

### Community 19 - "steps"
Cohesion: 0.23
Nodes (12): steps, steps, GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, steps, steps, env (+4 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 43 - "infrawatch_api/telemetry.py"
Cohesion: 0.10
Nodes (19): change_markers(), ChangeEvent, ChangeMarker, ingest_change(), ingest_logs(), ingest_metrics(), IngestResult, LogBatch (+11 more)

### Community 44 - "on"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 45 - "compose-smoke"
Cohesion: 0.67
Nodes (3): name, runs-on, compose-smoke

### Community 46 - "incidents.py"
Cohesion: 0.10
Nodes (23): load_roles(), require(), check(), change_severity(), change_status(), Detail, _detail(), get_incident() (+15 more)

### Community 47 - "collections_abc"
Cohesion: 0.10
Nodes (4): upgrade(), upgrade(), upgrade(), upgrade()

### Community 48 - "Incident lifecycle states and transitions (section 6.4)"
Cohesion: 0.22
Nodes (8): Incident lifecycle and transitions, Runbook process and controlled taxonomy, Controlled root cause taxonomy (seven categories), Incident lifecycle states and transitions (section 6.4), Runbook form fields and process (section 6.6), Seven-state incident lifecycle, Structured runbook mandatory fields, Severity and SLA defaults (P1-P4)

### Community 49 - "Sample"
Cohesion: 0.16
Nodes (4): Sample, Collector, collect_forever(), test_collector_reports_cpu_memory_disk_and_network()

### Community 50 - "layout.tsx"
Cohesion: 0.14
Nodes (10): nextConfig, dependencies, echarts@^6.1.0, next@16.4.5, react@19.3.0, react-dom@19.3.0, metadata, echarts (+2 more)

### Community 51 - "migrate"
Cohesion: 0.18
Nodes (11): condition, db, image, ports, command, depends_on, image, restart (+3 more)

### Community 52 - "logs/page.tsx"
Cohesion: 0.22
Nodes (6): @testing-library/react@^16.3.3, LEVELS, LogLine, LogsPage(), HomePage(), @testing-library/react

### Community 53 - "Architecture decision records index"
Cohesion: 0.12
Nodes (16): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, 0017. Object storage with RustFS, Consequences (+8 more)

### Community 54 - "AI layer design (section 6.7)"
Cohesion: 0.50
Nodes (3): AI layer two-tier design, AI layer design (section 6.7), AI layer (retrieval + reasoning)

### Community 56 - "api.ts"
Cohesion: 0.22
Nodes (14): AccessRequestsPage(), Decision(), approve(), reject(), Pending, ROLES, RequestAccessPage(), submit() (+6 more)

### Community 57 - "InfraWatch web application (Next.js)"
Cohesion: 0.29
Nodes (7): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout, Phase 1 implementation plan, Phase 1 scope (44 P1 checks plus G10.1/G10.2/walkthrough)

### Community 58 - "vitest"
Cohesion: 0.40
Nodes (3): vitest@^5.1.0, GET(), vitest

### Community 60 - "faults.py"
Cohesion: 0.24
Nodes (4): FaultActiveError, Faults, test_cpu_spike_starts_burners_and_stop_ends_them(), test_only_one_fault_runs_at_a_time_and_it_expires()

### Community 61 - "threading"
Cohesion: 0.12
Nodes (5): HealthHandler, stop_process(), base_url(), HealthHandler, base_url()

### Community 62 - "ci-passed"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, ci-passed

### Community 63 - "check-telemetry.sh"
Cohesion: 0.31
Nodes (7): api(), fault(), check-telemetry.sh script, sql(), utc_now(), wait_for_points_since(), wait_until()

### Community 64 - "environment"
Cohesion: 0.20
Nodes (10): RUSTFS_ACCESS_KEY, RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, RUSTFS_SECRET_KEY, environment, image, ports (+2 more)

### Community 65 - "depends_on"
Cohesion: 0.67
Nodes (3): depends_on, migrate, condition

### Community 66 - "Reporter"
Cohesion: 0.22
Nodes (7): now(), Reporter, sign(), test_flush_signs_changes_and_keeps_data_when_the_api_is_down(), handler(), scenario(), test_request_rate_uses_the_real_window_length()

### Community 67 - "test_permission_matrix.py"
Cohesion: 0.09
Nodes (26): _path(), test_each_role_gets_the_matrix_answer(), test_no_token_is_refused_before_any_role_check(), _url(), test_every_role_has_exactly_one_demo_user(), allows(), Capability, permits() (+18 more)

### Community 68 - "healthcheck"
Cohesion: 0.22
Nodes (10): environment, healthcheck, image, volumes, environment, AGENT_SERVICE, CHANGE_WEBHOOK_SECRET, INGEST_API_KEY (+2 more)

### Community 69 - "Gate G3 Incident lifecycle (9 checks)"
Cohesion: 0.17
Nodes (12): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Python collector agent SQLite buffer and retry policy, Decisions confirmed on 2026-11-09, M3 Identity, RBAC and audit foundation, M4 Incident lifecycle core, M6 Attachments, notifications and on-call, M8 Live updates and thin-slice end-to-end test, WebSocket sequence numbers, replay and back-pressure policy (+4 more)

### Community 70 - "environment"
Cohesion: 0.40
Nodes (5): environment, DB_APP_PASSWORD, DB_OWNER_PASSWORD, POSTGRES_INITDB_ARGS, POSTGRES_PASSWORD

### Community 71 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.28
Nodes (8): infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation, ADR 0013: Standalone ticketing with optional ServiceNow sync

### Community 72 - "test_ingest_auth.py"
Cohesion: 0.07
Nodes (19): create_app(), health(), HealthResponse, lifespan(), test_me_needs_a_bearer_token(), test_refresh_and_logout_need_the_csrf_header(), app(), client() (+11 more)

### Community 73 - "infrawatch-api FastAPI service"
Cohesion: 0.32
Nodes (8): infrawatch-api FastAPI service, infrawatch-demo-app, Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan, Shared python.Dockerfile

### Community 74 - "infrawatch_demo_app/telemetry.py"
Cohesion: 0.21
Nodes (3): summarise(), test_summarise_of_an_empty_window_has_no_latency(), test_summarise_reports_rate_errors_and_p95()

### Community 75 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.29
Nodes (8): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, WebSocket gateway, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log, PostgreSQL LISTEN/NOTIFY channel

### Community 76 - "Buffer"
Cohesion: 0.21
Nodes (3): Buffer, deliver_forever(), flush()

### Community 77 - "check-incidents.sh"
Cohesion: 0.52
Nodes (6): code(), expect(), fail(), move(), check-incidents.sh script, token()

### Community 87 - "environment"
Cohesion: 0.33
Nodes (6): environment, DATABASE_URL, DEMO_USER_PASSWORD, INGEST_API_KEYS, JWT_SECRET, environment

### Community 89 - "login/page.tsx"
Cohesion: 0.83
Nodes (3): LoginPage(), submit(), signIn()

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-api`, `infrawatch-core`, `infrawatch-agent`, `infrawatch-demo-app`, `infrawatch-worker` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 334 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `post()` connect `auth.py` to `infrawatch_api/telemetry.py`, `test_agent_entrypoint.py`, `Buffer`, `incidents.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `Capability` (e.g. with `require()` and `approve_request()`) actually correct?**
  _`Capability` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-api`, `infrawatch-core`, `infrawatch-agent` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.08870967741935484 - nodes in this community are weakly interconnected._
- **Why does `Architecture decision records index` connect `Architecture decision records index` to `Contributing to InfraWatch`, `InfraWatch 2.0 README overview`, `ADR 0011: Authentication and tokens`, `ADR 0008: Job queue and transactional outbox in PostgreSQL`, `infrawatch-api FastAPI service`, `ADR 0009: WebSockets for real-time updates`, `InfraWatch web application (Next.js)`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Sample` (e.g. with `Collector` and `deliver_forever()`) actually correct?**
  _`Sample` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `InfraWatch 2.0 README overview` be split into smaller, more focused modules?**
  _Cohesion score 0.08923076923076922 - nodes in this community are weakly interconnected._
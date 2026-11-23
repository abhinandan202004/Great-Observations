# Graph Report - Great-Observations  (2026-11-24)

## Corpus Check
- 149 files · ~54,520 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 1230 nodes · 2482 edges · 113 communities (67 shown, 46 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 154 edges (avg confidence: 0.9)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `4a5abd21`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- devDependencies
- Contributing to InfraWatch
- InfraWatch 2.0 README overview
- infrawatch_worker/__main__.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- auth.py
- with
- interval
- args
- eslint.config.mjs
- Workflow Permissions
- compose.yaml
- infrawatch_api/__main__.py
- jobs
- CI Web Job
- scripts
- infrawatch_demo_app/telemetry.py
- infrawatch_agent/__main__.py
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
- alerting.py
- Workspace Root
- init-infrawatch.sh
- infrawatch_api/telemetry.py
- on
- compose-smoke
- incidents.py
- collections_abc
- Incident lifecycle states and transitions (section 6.4)
- infrawatch_api/oncall.py
- dependencies
- migrate
- vitest
- Architecture decision records index
- AI layer design (section 6.7)
- getJson
- incident.tsx
- InfraWatch web application (Next.js)
- route.test.ts
- check-audit.sh
- vitest.config.mts
- mail.py
- ci-passed
- check-telemetry.sh
- environment
- depends_on
- drafts/page.tsx
- test_permission_matrix.py
- healthcheck
- Gate G3 Incident lifecycle (9 checks)
- environment
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- accounts.py
- infrawatch-api FastAPI service
- engines
- ADR 0009: WebSockets for real-time updates
- timers
- check-incidents.sh
- check-auth.sh
- infrawatch_demo_app/main.py
- check-notifications.sh
- Faults
- next
- postJson
- check-alerts.sh
- react
- sqlalchemy_ext_asyncio
- create_app
- check-alert-baseline.sh
- login/page.tsx
- alerts.py
- migrate
- x-python-health
- HealthHandler

## God Nodes (most connected - your core abstractions)
1. `record()` - 27 edges
2. `Capability` - 23 edges
3. `getJson()` - 20 edges
4. `InfraWatch 2.0 README overview` - 20 edges
5. `Architecture decision records index` - 20 edges
6. `Sample` - 19 edges
7. `permits()` - 18 edges
8. `react` - 18 edges
9. `Buffer` - 17 edges
10. `current_user_id()` - 17 edges

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

## Communities (113 total, 46 thin omitted)

### Community 0 - "devDependencies"
Cohesion: 0.15
Nodes (18): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+10 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.21
Nodes (11): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Working practices (branches, commits, server-side enforcement), Permission policy in infrawatch-core, M0 Repository foundation and CI, M10 Phase 1 hardening and release (+3 more)

### Community 2 - "InfraWatch 2.0 README overview"
Cohesion: 0.09
Nodes (23): Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks, Compose architecture and principal data entities (section 7), Business case (problem, value, portfolio) (+15 more)

### Community 3 - "infrawatch_worker/__main__.py"
Cohesion: 0.15
Nodes (5): deliver(), smtp_sender(), main(), periodic(), run()

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "auth.py"
Cohesion: 0.06
Nodes (36): check_password(), _hash_refresh(), issue_access_token(), login(), LoginRequest, logout(), Me, me() (+28 more)

### Community 7 - "with"
Cohesion: 0.29
Nodes (7): with, cache, cache-dependency-path, enable-cache, fetch-depth, node-version, version

### Community 8 - "interval"
Cohesion: 0.16
Nodes (28): healthcheck, healthcheck, healthcheck, image, volumes, healthcheck, image, ports (+20 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

### Community 10 - "eslint.config.mjs"
Cohesion: 0.33
Nodes (5): eslintConfig, eslint@^9.39.5, eslint-config-next@16.4.5, eslint, eslint-config-next

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.20
Nodes (9): name, services, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context (+1 more)

### Community 13 - "infrawatch_api/__main__.py"
Cohesion: 0.17
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

### Community 17 - "infrawatch_demo_app/telemetry.py"
Cohesion: 0.13
Nodes (10): now(), Reporter, sign(), summarise(), test_flush_signs_changes_and_keeps_data_when_the_api_is_down(), handler(), scenario(), test_request_rate_uses_the_real_window_length() (+2 more)

### Community 18 - "infrawatch_agent/__main__.py"
Cohesion: 0.05
Nodes (32): Buffer, Sample, Collector, backoff_delay(), collect_forever(), deliver_forever(), flush(), HealthHandler (+24 more)

### Community 19 - "steps"
Cohesion: 0.23
Nodes (12): steps, steps, GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, steps, steps, env (+4 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 27 - "API-Core Dependency"
Cohesion: 0.67
Nodes (3): infrawatch-api, infrawatch-core, infrawatch-worker

### Community 40 - "alerting.py"
Cohesion: 0.23
Nodes (12): breaches(), Comparator, firing_since(), Rule, end(), series(), test_a_breach_lasting_the_duration_fires_from_its_first_sample(), test_a_breach_shorter_than_the_duration_does_not_fire() (+4 more)

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
Cohesion: 0.06
Nodes (55): load_roles(), require(), check(), record(), current_user_id(), AlertRule, AlertRuleIn, dismiss_draft() (+47 more)

### Community 47 - "collections_abc"
Cohesion: 0.10
Nodes (7): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade()

### Community 48 - "Incident lifecycle states and transitions (section 6.4)"
Cohesion: 0.22
Nodes (8): Incident lifecycle and transitions, Runbook process and controlled taxonomy, Controlled root cause taxonomy (seven categories), Incident lifecycle states and transitions (section 6.4), Runbook form fields and process (section 6.6), Seven-state incident lifecycle, Structured runbook mandatory fields, Severity and SLA defaults (P1-P4)

### Community 49 - "infrawatch_api/oncall.py"
Cohesion: 0.10
Nodes (18): list_on_call(), on_call_now(), Person, RotationIn, RotationOut, rotations(), set_rotation(), TeamOnCall (+10 more)

### Community 50 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, echarts@^6.1.0, next@16.4.5, react@19.3.0, react-dom@19.3.0, echarts, react-dom

### Community 51 - "migrate"
Cohesion: 0.17
Nodes (12): environment, ALERT_EVAL_SECONDS, DATABASE_URL, DEMO_USER_PASSWORD, INGEST_API_KEYS, JWT_SECRET, MAIL_FROM, SMTP_HOST (+4 more)

### Community 52 - "vitest"
Cohesion: 0.22
Nodes (7): @testing-library/react@^16.3.3, vitest@^5.1.0, summary, timer, HomePage(), @testing-library/react, vitest

### Community 53 - "Architecture decision records index"
Cohesion: 0.12
Nodes (16): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, 0017. Object storage with RustFS, Consequences (+8 more)

### Community 54 - "AI layer design (section 6.7)"
Cohesion: 0.50
Nodes (3): AI layer two-tier design, AI layer design (section 6.7), AI layer (retrieval + reasoning)

### Community 55 - "getJson"
Cohesion: 0.15
Nodes (14): Policy, SlaPolicyPage(), RaiseIncidentPage(), LEVELS, LogLine, LogsPage(), TelemetryPage(), load() (+6 more)

### Community 56 - "incident.tsx"
Cohesion: 0.13
Nodes (20): Clock(), Act, Incident(), StatusBar(), Task(), Work(), IncidentPage(), IncidentsPage() (+12 more)

### Community 57 - "InfraWatch web application (Next.js)"
Cohesion: 0.29
Nodes (7): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout, Phase 1 implementation plan, Phase 1 scope (44 P1 checks plus G10.1/G10.2/walkthrough)

### Community 60 - "vitest.config.mts"
Cohesion: 0.40
Nodes (4): vite-tsconfig-paths@^6.1.1, @vitejs/plugin-react@^6.2.1, vite-tsconfig-paths, @vitejs/plugin-react

### Community 61 - "mail.py"
Cohesion: 0.14
Nodes (6): message(), retry_delay(), row(), test_no_cc_header_when_nobody_is_on_call(), test_retries_back_off_from_thirty_seconds_to_an_hour(), test_the_message_carries_group_to_on_call_cc_and_a_stable_id()

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
Cohesion: 0.29
Nodes (7): depends_on, image, ports, migrate, condition, api, depends_on

### Community 66 - "drafts/page.tsx"
Cohesion: 0.22
Nodes (13): AlertFigure(), DraftCard(), raise(), send(), DraftsPage(), Change, Chart(), chartOption() (+5 more)

### Community 67 - "test_permission_matrix.py"
Cohesion: 0.11
Nodes (25): _path(), test_each_role_gets_the_matrix_answer(), test_no_token_is_refused_before_any_role_check(), _url(), allows(), Capability, permits(), Relation (+17 more)

### Community 68 - "healthcheck"
Cohesion: 0.25
Nodes (9): environment, image, volumes, environment, AGENT_SERVICE, CHANGE_WEBHOOK_SECRET, INGEST_API_KEY, INGEST_URL (+1 more)

### Community 69 - "Gate G3 Incident lifecycle (9 checks)"
Cohesion: 0.17
Nodes (12): Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Python collector agent SQLite buffer and retry policy, Decisions confirmed on 2026-11-09, M3 Identity, RBAC and audit foundation, M4 Incident lifecycle core, M6 Attachments, notifications and on-call, M8 Live updates and thin-slice end-to-end test, WebSocket sequence numbers, replay and back-pressure policy (+4 more)

### Community 70 - "environment"
Cohesion: 0.40
Nodes (5): environment, DB_APP_PASSWORD, DB_OWNER_PASSWORD, POSTGRES_INITDB_ARGS, POSTGRES_PASSWORD

### Community 71 - "ADR 0008: Job queue and transactional outbox in PostgreSQL"
Cohesion: 0.28
Nodes (8): infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, InfraWatch incident ticketing as system of record, Optional ServiceNow Table API synchronisation, ADR 0013: Standalone ticketing with optional ServiceNow sync

### Community 72 - "accounts.py"
Cohesion: 0.11
Nodes (17): post(), AccessRequestIn, ApprovalIn, approve_request(), create_user(), _create_user(), pending_requests(), reject_request() (+9 more)

### Community 73 - "infrawatch-api FastAPI service"
Cohesion: 0.32
Nodes (8): infrawatch-api FastAPI service, infrawatch-demo-app, Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan, Shared python.Dockerfile

### Community 75 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.29
Nodes (8): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, WebSocket gateway, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log, PostgreSQL LISTEN/NOTIFY channel

### Community 76 - "timers"
Cohesion: 0.12
Nodes (18): classify(), Move, Severity, Status, TransitionError, Policy, Timer, _timer() (+10 more)

### Community 77 - "check-incidents.sh"
Cohesion: 0.38
Nodes (9): code(), expect(), fail(), move(), post(), check-incidents.sh script, team_of(), token() (+1 more)

### Community 81 - "infrawatch_demo_app/main.py"
Cohesion: 0.27
Nodes (5): checkout(), generate_traffic(), lifespan(), _NoHealthFilter, report()

### Community 84 - "check-notifications.sh"
Cohesion: 0.28
Nodes (13): addressed(), as(), code(), fail(), mail(), move(), put(), check-notifications.sh script (+5 more)

### Community 85 - "Faults"
Cohesion: 0.38
Nodes (4): FaultActiveError, Faults, test_cpu_spike_starts_burners_and_stop_ends_them(), test_only_one_fault_runs_at_a_time_and_it_expires()

### Community 86 - "next"
Cohesion: 0.29
Nodes (7): nextConfig, metadata, RootLayout(), CurrentNav(), LINKS, NavLinks(), next

### Community 87 - "postJson"
Cohesion: 0.29
Nodes (9): AccessRequestsPage(), Decision(), approve(), reject(), Pending, ROLES, RequestAccessPage(), submit() (+1 more)

### Community 89 - "check-alerts.sh"
Cohesion: 0.44
Nodes (7): cleanup(), fail(), fault(), check-alerts.sh script, sql(), token(), wait_for()

### Community 90 - "react"
Cohesion: 0.46
Nodes (6): linkError(), pageAnnouncer(), spoken(), Form(), useUserInvalid(), react

### Community 95 - "create_app"
Cohesion: 0.31
Nodes (8): CheckoutResponse, create_app(), health(), post_checkout(), start_fault(), stop_fault(), FaultResponse, HealthResponse

### Community 96 - "check-alert-baseline.sh"
Cohesion: 0.70
Nodes (4): cleanup(), fail(), check-alert-baseline.sh script, sql()

### Community 98 - "login/page.tsx"
Cohesion: 0.83
Nodes (3): LoginPage(), submit(), signIn()

### Community 106 - "migrate"
Cohesion: 0.29
Nodes (7): condition, db, command, depends_on, image, restart, migrate

### Community 108 - "x-python-health"
Cohesion: 0.29
Nodes (7): x-python-health, interval, retries, start_interval, start_period, test, timeout

## Knowledge Gaps
- **59 isolated node(s):** `infrawatch-api`, `infrawatch-worker`, `infrawatch-agent`, `infrawatch-demo-app`, `infrawatch-workspace` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 406 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `record()` connect `incidents.py` to `accounts.py`, `infrawatch_api/oncall.py`, `infrawatch_agent/__main__.py`, `auth.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Capability` (e.g. with `approve_request()` and `create_user()`) actually correct?**
  _`Capability` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-api`, `infrawatch-worker`, `infrawatch-agent` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Why does `current_user_id()` connect `incidents.py` to `infrawatch_api/oncall.py`, `auth.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Should `InfraWatch 2.0 README overview` be split into smaller, more focused modules?**
  _Cohesion score 0.08923076923076922 - nodes in this community are weakly interconnected._
- **Why does `require()` connect `incidents.py` to `accounts.py`, `infrawatch_api/oncall.py`, `test_permission_matrix.py`, `infrawatch_api/telemetry.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
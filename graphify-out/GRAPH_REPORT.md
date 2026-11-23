# Graph Report - Great-Observations  (2026-11-24)

## Corpus Check
- 177 files · ~66,844 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 1479 nodes · 3101 edges · 134 communities (74 shown, 60 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 170 edges (avg confidence: 0.9)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `4321ac2e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- Contributing to InfraWatch
- InfraWatch 2.0 README overview
- infrawatch_worker/__main__.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- auth.py
- with
- interval
- args
- incidents.py
- Workflow Permissions
- compose.yaml
- infrawatch_api/__main__.py
- jobs
- CI Web Job
- drafts.py
- infrawatch_agent/__main__.py
- Sample
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
- test_ingest_auth.py
- sqlalchemy
- Incident lifecycle states and transitions (section 6.4)
- HealthHandler
- migrate
- oncall/page.tsx
- Architecture decision records index
- AI layer design (section 6.7)
- getJson
- incident.tsx
- InfraWatch web application (Next.js)
- infrawatch_demo_app/main.py
- check-audit.sh
- infrawatch_api/oncall.py
- ci-passed
- check-telemetry.sh
- environment
- depends_on
- drafts/page.tsx
- Capability
- healthcheck
- Gate G3 Incident lifecycle (9 checks)
- environment
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- json
- infrawatch-api FastAPI service
- attachments.py
- ADR 0009: WebSockets for real-time updates
- timers
- check-incidents.sh
- check-auth.sh
- infrawatch_demo_app/telemetry.py
- vitest
- check-notifications.sh
- next
- attachments.tsx
- check-escalation.sh
- check-alerts.sh
- mail.py
- accounts.py
- attachments.py
- check-alert-baseline.sh
- check-attachments.sh
- runbook.tsx
- migrate
- faults.py
- check-runbooks.sh
- seed.py
- sniff
- env.py
- runbooks.py
- infrawatch_demo_app/telemetry.py
- create_app
- faults.py

## God Nodes (most connected - your core abstractions)
1. `record()` - 32 edges
2. `getJson()` - 31 edges
3. `Capability` - 29 edges
4. `current_user_id()` - 25 edges
5. `postJson()` - 25 edges
6. `react` - 22 edges
7. `get()` - 21 edges
8. `permits()` - 21 edges
9. `InfraWatch 2.0 README overview` - 20 edges
10. `Architecture decision records index` - 20 edges

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

## Communities (134 total, 60 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.05
Nodes (46): eslintConfig, dependencies, echarts@^6.1.0, next@16.4.5, react@19.3.0, react-dom@19.3.0, devDependencies, eslint@^9.39.5 (+38 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.21
Nodes (11): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Working practices (branches, commits, server-side enforcement), Permission policy in infrawatch-core, M0 Repository foundation and CI, M10 Phase 1 hardening and release (+3 more)

### Community 2 - "InfraWatch 2.0 README overview"
Cohesion: 0.09
Nodes (23): Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks, Compose architecture and principal data entities (section 7), Business case (problem, value, portfolio) (+15 more)

### Community 3 - "infrawatch_worker/__main__.py"
Cohesion: 0.12
Nodes (7): deliver(), smtp_sender(), HealthHandler, main(), periodic(), run(), base_url()

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "auth.py"
Cohesion: 0.13
Nodes (17): check_password(), current_user_id(), _hash_refresh(), issue_access_token(), login(), LoginRequest, logout(), Me (+9 more)

### Community 7 - "with"
Cohesion: 0.29
Nodes (7): with, cache, cache-dependency-path, enable-cache, fetch-depth, node-version, version

### Community 8 - "interval"
Cohesion: 0.16
Nodes (28): healthcheck, healthcheck, healthcheck, image, volumes, healthcheck, image, ports (+20 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

### Community 10 - "incidents.py"
Cohesion: 0.14
Nodes (18): AssigneeIn, CheckIn, ChecklistItem, ChecklistItemIn, EscalationRecord, list_teams(), Member, open_incident() (+10 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.12
Nodes (16): name, services, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context (+8 more)

### Community 13 - "infrawatch_api/__main__.py"
Cohesion: 0.23
Nodes (3): main(), _NoHealthFilter, main()

### Community 14 - "jobs"
Cohesion: 0.22
Nodes (8): concurrency, cancel-in-progress, group, jobs, python, name, name, runs-on

### Community 15 - "CI Web Job"
Cohesion: 0.29
Nodes (7): run, web, working-directory, defaults, name, runs-on, steps

### Community 16 - "drafts.py"
Cohesion: 0.17
Nodes (11): AlertRule, AlertRuleIn, dismiss_draft(), Draft, DraftRaiseIn, list_drafts(), list_rules(), _locked_draft() (+3 more)

### Community 17 - "infrawatch_agent/__main__.py"
Cohesion: 0.11
Nodes (9): Collector, backoff_delay(), collect_forever(), deliver_forever(), main(), post(), stop_process(), test_backoff_stays_between_one_and_sixty_seconds() (+1 more)

### Community 18 - "Sample"
Cohesion: 0.14
Nodes (16): Buffer, Sample, flush(), CountingCollector, samples(), status_error(), StopReadingsError, test_buffer_drops_oldest_when_full_and_reports_count() (+8 more)

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
Cohesion: 0.09
Nodes (20): evaluate(), _fire(), message(), retry_delay(), row(), test_no_cc_header_when_nobody_is_on_call(), test_retries_back_off_from_thirty_seconds_to_an_hour(), test_the_message_carries_group_to_on_call_cc_and_a_stable_id() (+12 more)

### Community 43 - "infrawatch_api/telemetry.py"
Cohesion: 0.06
Nodes (26): pending_requests(), _bucket(), _client(), get(), _get(), put(), _put(), change_markers() (+18 more)

### Community 44 - "on"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 45 - "compose-smoke"
Cohesion: 0.67
Nodes (3): name, runs-on, compose-smoke

### Community 46 - "test_ingest_auth.py"
Cohesion: 0.15
Nodes (16): client(), test_app_refuses_to_start_with_a_short_secret(), test_me_needs_a_bearer_token(), test_refresh_and_logout_need_the_csrf_header(), app(), client(), signed(), test_change_webhook_rejects_a_bad_signature() (+8 more)

### Community 47 - "sqlalchemy"
Cohesion: 0.09
Nodes (10): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade() (+2 more)

### Community 48 - "Incident lifecycle states and transitions (section 6.4)"
Cohesion: 0.22
Nodes (8): Incident lifecycle and transitions, Runbook process and controlled taxonomy, Controlled root cause taxonomy (seven categories), Incident lifecycle states and transitions (section 6.4), Runbook form fields and process (section 6.6), Seven-state incident lifecycle, Structured runbook mandatory fields, Severity and SLA defaults (P1-P4)

### Community 51 - "migrate"
Cohesion: 0.13
Nodes (16): environment, ALERT_EVAL_SECONDS, DATABASE_URL, DEMO_USER_PASSWORD, INGEST_API_KEYS, JWT_SECRET, MAIL_FROM, S3_ACCESS_KEY (+8 more)

### Community 52 - "oncall/page.tsx"
Cohesion: 0.18
Nodes (14): OnCallPage(), TeamRotation(), shift(), Undelivered(), Team, move(), Person, TeamOnCall (+6 more)

### Community 53 - "Architecture decision records index"
Cohesion: 0.12
Nodes (16): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, 0017. Object storage with RustFS, Consequences (+8 more)

### Community 54 - "AI layer design (section 6.7)"
Cohesion: 0.50
Nodes (3): AI layer two-tier design, AI layer design (section 6.7), AI layer (retrieval + reasoning)

### Community 55 - "getJson"
Cohesion: 0.18
Nodes (15): Policy, SlaPolicyPage(), RaiseIncidentPage(), TelemetryPage(), load(), call(), formatTime(), getJson() (+7 more)

### Community 56 - "incident.tsx"
Cohesion: 0.13
Nodes (20): Clock(), Act, Incident(), StatusBar(), Task(), Work(), IncidentPage(), IncidentsPage() (+12 more)

### Community 57 - "InfraWatch web application (Next.js)"
Cohesion: 0.29
Nodes (7): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout, Phase 1 implementation plan, Phase 1 scope (44 P1 checks plus G10.1/G10.2/walkthrough)

### Community 58 - "infrawatch_demo_app/main.py"
Cohesion: 0.24
Nodes (5): checkout(), generate_traffic(), lifespan(), _NoHealthFilter, report()

### Community 61 - "infrawatch_api/oncall.py"
Cohesion: 0.11
Nodes (20): _rotations(), sweep(), Escalation, next_escalation(), current_shift(), Rotation, Shift, at() (+12 more)

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
Cohesion: 0.21
Nodes (14): AlertFigure(), PointsFigure(), DraftCard(), raise(), send(), DraftsPage(), Change, Chart() (+6 more)

### Community 67 - "Capability"
Cohesion: 0.06
Nodes (51): load_roles(), check(), _working_on(), add_checklist_item(), add_team(), assign(), change_severity(), change_status() (+43 more)

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

### Community 72 - "json"
Cohesion: 0.21
Nodes (4): test_health_reports_ok(), test_unknown_path_is_not_found(), test_health_reports_ok(), test_unknown_path_is_not_found()

### Community 73 - "infrawatch-api FastAPI service"
Cohesion: 0.32
Nodes (8): infrawatch-api FastAPI service, infrawatch-demo-app, Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan, Shared python.Dockerfile

### Community 74 - "attachments.py"
Cohesion: 0.16
Nodes (11): _add(), attach_file(), attach_logs(), attach_note(), attach_snapshot(), Attachment, download_file(), list_attachments() (+3 more)

### Community 75 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.29
Nodes (8): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, WebSocket gateway, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log, PostgreSQL LISTEN/NOTIFY channel

### Community 76 - "timers"
Cohesion: 0.12
Nodes (18): classify(), Move, Severity, Status, TransitionError, Policy, Timer, _timer() (+10 more)

### Community 77 - "check-incidents.sh"
Cohesion: 0.38
Nodes (9): code(), expect(), fail(), move(), post(), check-incidents.sh script, team_of(), token() (+1 more)

### Community 81 - "infrawatch_demo_app/telemetry.py"
Cohesion: 0.21
Nodes (7): now(), Reporter, test_flush_signs_changes_and_keeps_data_when_the_api_is_down(), handler(), scenario(), test_request_rate_uses_the_real_window_length(), scenario()

### Community 82 - "vitest"
Cohesion: 0.10
Nodes (12): @testing-library/react@^16.3.3, summary, timer, version, LEVELS, LogLine, LogsPage(), asha (+4 more)

### Community 84 - "check-notifications.sh"
Cohesion: 0.28
Nodes (13): addressed(), as(), code(), fail(), mail(), move(), put(), check-notifications.sh script (+5 more)

### Community 86 - "next"
Cohesion: 0.21
Nodes (10): nextConfig, metadata, RootLayout(), LoginPage(), submit(), CurrentNav(), LINKS, NavLinks() (+2 more)

### Community 87 - "attachments.tsx"
Cohesion: 0.11
Nodes (29): AccessRequestsPage(), Decision(), approve(), reject(), Pending, ROLES, Added, Attachments() (+21 more)

### Community 88 - "check-escalation.sh"
Cohesion: 0.40
Nodes (8): as(), backdate(), escalations(), fail(), raise(), check-escalation.sh script, sql(), token()

### Community 89 - "check-alerts.sh"
Cohesion: 0.44
Nodes (7): cleanup(), fail(), fault(), check-alerts.sh script, sql(), token(), wait_for()

### Community 92 - "accounts.py"
Cohesion: 0.22
Nodes (10): AccessRequestIn, ApprovalIn, approve_request(), create_user(), _create_user(), reject_request(), request_access(), UserIn (+2 more)

### Community 95 - "attachments.py"
Cohesion: 0.12
Nodes (7): require(), _safe_name(), create_app(), health(), HealthResponse, lifespan(), test_only_a_clean_base_name_is_kept()

### Community 96 - "check-alert-baseline.sh"
Cohesion: 0.70
Nodes (4): cleanup(), fail(), check-alert-baseline.sh script, sql()

### Community 98 - "check-attachments.sh"
Cohesion: 0.35
Nodes (9): ago(), as(), attachments(), code(), expect(), fail(), check-attachments.sh script, token() (+1 more)

### Community 103 - "runbook.tsx"
Cohesion: 0.16
Nodes (17): Done, ReviewForm(), review(), RunbookForm(), submit(), RunbookPanel(), TEXT_FIELDS, VersionView() (+9 more)

### Community 104 - "migrate"
Cohesion: 0.29
Nodes (7): condition, db, command, depends_on, image, restart, migrate

### Community 106 - "faults.py"
Cohesion: 0.38
Nodes (4): FaultActiveError, Faults, test_cpu_spike_starts_burners_and_stop_ends_them(), test_only_one_fault_runs_at_a_time_and_it_expires()

### Community 107 - "check-runbooks.sh"
Cohesion: 0.31
Nodes (11): as(), code(), expect(), fail(), move(), raise(), resolve(), review() (+3 more)

### Community 108 - "seed.py"
Cohesion: 0.18
Nodes (5): DemoRule, DemoService, DemoUser, main(), seed()

### Community 112 - "sniff"
Cohesion: 0.36
Nodes (3): sniff(), test_allowed_files_are_recognised_by_their_bytes(), test_everything_else_is_refused()

### Community 118 - "runbooks.py"
Cohesion: 0.07
Nodes (31): list_on_call(), on_call_now(), Person, RotationIn, RotationOut, rotations(), set_rotation(), TeamOnCall (+23 more)

### Community 119 - "infrawatch_demo_app/telemetry.py"
Cohesion: 0.23
Nodes (4): sign(), summarise(), test_summarise_of_an_empty_window_has_no_latency(), test_summarise_reports_rate_errors_and_p95()

### Community 121 - "create_app"
Cohesion: 0.31
Nodes (8): CheckoutResponse, create_app(), health(), post_checkout(), start_fault(), stop_fault(), FaultResponse, HealthResponse

## Knowledge Gaps
- **59 isolated node(s):** `infrawatch-api`, `infrawatch-worker`, `infrawatch-agent`, `infrawatch-demo-app`, `infrawatch-workspace` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 474 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **60 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `record()` connect `accounts.py` to `Capability`, `auth.py`, `json`, `attachments.py`, `incidents.py`, `drafts.py`, `runbooks.py`, `attachments.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Capability` (e.g. with `add_checklist_item()` and `add_team()`) actually correct?**
  _`Capability` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-api`, `infrawatch-worker`, `infrawatch-agent` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05254901960784314 - nodes in this community are weakly interconnected._
- **Why does `react` connect `incident.tsx` to `package.json`, `drafts/page.tsx`, `runbook.tsx`, `vitest`, `oncall/page.tsx`, `attachments.tsx`, `getJson`, `next`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Should `InfraWatch 2.0 README overview` be split into smaller, more focused modules?**
  _Cohesion score 0.08923076923076922 - nodes in this community are weakly interconnected._
- **Why does `Capability` connect `Capability` to `attachments.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
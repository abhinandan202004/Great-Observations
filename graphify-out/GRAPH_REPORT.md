# Graph Report - Great-Observations  (2026-11-27)

## Corpus Check
- 190 files · ~72,400 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 1575 nodes · 3410 edges · 109 communities (83 shown, 26 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 221 edges (avg confidence: 0.92)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `f79dd6e4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- Contributing to InfraWatch
- InfraWatch 2.0 README overview
- infrawatch_worker/__main__.py
- ADR 0011: Authentication and tokens
- TypeScript Compiler Options
- live.py
- with
- interval
- args
- incidents.py
- Workflow Permissions
- compose.yaml
- infrawatch_api/__main__.py
- ci.yml
- CI Web Job
- drafts.py
- infrawatch_agent/__main__.py
- getJson
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
- runbook.tsx
- jobs
- test_ingest_auth.py
- sqlalchemy
- Incident lifecycle states and transitions (section 6.4)
- change_status
- stack.ts
- migrate
- oncall/page.tsx
- Architecture decision records index
- AI layer design (section 6.7)
- api.ts
- incident.tsx
- InfraWatch web application (Next.js)
- infrawatch_demo_app/main.py
- check-audit.sh
- vitest
- infrawatch_api/oncall.py
- ci-passed
- check-telemetry.sh
- environment
- depends_on
- drafts/page.tsx
- permits
- healthcheck
- Gate G3 Incident lifecycle (9 checks)
- environment
- ADR 0008: Job queue and transactional outbox in PostgreSQL
- test_auth.py
- infrawatch-api FastAPI service
- attachments.py
- ADR 0009: WebSockets for real-time updates
- timers
- check-incidents.sh
- scripts
- Hub
- check-auth.sh
- infrawatch_demo_app/telemetry.py
- dependencies
- eslint.config.mjs
- check-notifications.sh
- record
- next
- attachments.tsx
- check-escalation.sh
- check-alerts.sh
- vitest.config.mts
- mail.py
- infrawatch_api/main.py
- check-alert-baseline.sh
- check-attachments.sh
- runbook.tsx
- migrate
- faults.py
- check-runbooks.sh
- auth.py
- current_user_id
- live.ts
- faults.py
- check-live.py
- current_user_id
- runbooks.py
- publish
- runbook_approved
- env.py

## God Nodes (most connected - your core abstractions)
1. `Capability` - 38 edges
2. `record()` - 32 edges
3. `getJson()` - 31 edges
4. `current_user_id()` - 25 edges
5. `postJson()` - 25 edges
6. `Role` - 25 edges
7. `react` - 23 edges
8. `change_status()` - 21 edges
9. `get()` - 21 edges
10. `permits()` - 21 edges

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

## Communities (109 total, 26 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.13
Nodes (20): devDependencies, jsdom@^29.1.1, @testing-library/dom@^10.4.2, @types/node@^22.20.5, @types/react@^19, @types/react-dom@^19, typescript@^5, @vitest/coverage-v8@^5.1.0 (+12 more)

### Community 1 - "Contributing to InfraWatch"
Cohesion: 0.21
Nodes (11): Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Working practices (branches, commits, server-side enforcement), Permission policy in infrawatch-core, M0 Repository foundation and CI, M10 Phase 1 hardening and release (+3 more)

### Community 2 - "InfraWatch 2.0 README overview"
Cohesion: 0.09
Nodes (23): Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks, Compose architecture and principal data entities (section 7), Business case (problem, value, portfolio) (+15 more)

### Community 3 - "infrawatch_worker/__main__.py"
Cohesion: 0.13
Nodes (6): deliver(), smtp_sender(), HealthHandler, main(), periodic(), run()

### Community 4 - "ADR 0011: Authentication and tokens"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "live.py"
Cohesion: 0.18
Nodes (7): allowed_origins(), Client, _close(), gateway(), _send(), _subscribe(), Subscription

### Community 7 - "with"
Cohesion: 0.20
Nodes (10): with, cache, cache-dependency-path, enable-cache, fetch-depth, name, node-version, path (+2 more)

### Community 8 - "interval"
Cohesion: 0.16
Nodes (28): healthcheck, healthcheck, healthcheck, image, volumes, healthcheck, image, ports (+20 more)

### Community 9 - "args"
Cohesion: 0.32
Nodes (12): build, build, MODULE, PACKAGE, args, context, dockerfile, build (+4 more)

### Community 10 - "incidents.py"
Cohesion: 0.15
Nodes (20): AssigneeIn, CheckIn, ChecklistItem, ChecklistItemIn, EscalationRecord, list_sla_policies(), list_teams(), Member (+12 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.12
Nodes (16): name, services, volumes, agent-buffer, db-data, objectstore-data, x-api-build, context (+8 more)

### Community 13 - "infrawatch_api/__main__.py"
Cohesion: 0.17
Nodes (4): stop_process(), main(), _NoHealthFilter, main()

### Community 14 - "ci.yml"
Cohesion: 0.20
Nodes (9): concurrency, cancel-in-progress, group, name, on, pull_request, push, branches (+1 more)

### Community 15 - "CI Web Job"
Cohesion: 0.29
Nodes (7): run, web, working-directory, defaults, name, runs-on, steps

### Community 16 - "drafts.py"
Cohesion: 0.17
Nodes (12): AlertRule, AlertRuleIn, dismiss_draft(), Draft, DraftRaiseIn, list_drafts(), list_rules(), _locked_draft() (+4 more)

### Community 17 - "infrawatch_agent/__main__.py"
Cohesion: 0.05
Nodes (33): Buffer, Sample, Collector, backoff_delay(), collect_forever(), deliver_forever(), flush(), HealthHandler (+25 more)

### Community 18 - "getJson"
Cohesion: 0.17
Nodes (13): SlaPolicyPage(), LEVELS, LogLine, LogsPage(), Change, Chart(), chartOption(), Point (+5 more)

### Community 19 - "steps"
Cohesion: 0.22
Nodes (10): steps, E2E_BASE_URL, GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, steps, env, if (+2 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

### Community 27 - "API-Core Dependency"
Cohesion: 0.67
Nodes (3): infrawatch-api, infrawatch-core, infrawatch-worker

### Community 40 - "alerting.py"
Cohesion: 0.09
Nodes (17): evaluate(), _fire(), _rotations(), sweep(), publish(), breaches(), Comparator, firing_since() (+9 more)

### Community 43 - "infrawatch_api/telemetry.py"
Cohesion: 0.10
Nodes (20): get(), change_markers(), ChangeEvent, ChangeMarker, ingest_change(), ingest_logs(), ingest_metrics(), IngestResult (+12 more)

### Community 44 - "runbook.tsx"
Cohesion: 0.18
Nodes (15): Done, ReviewForm(), review(), RunbookForm(), submit(), RunbookPanel(), TEXT_FIELDS, VersionView() (+7 more)

### Community 45 - "jobs"
Cohesion: 0.29
Nodes (7): name, runs-on, jobs, compose-smoke, python, name, runs-on

### Community 46 - "test_ingest_auth.py"
Cohesion: 0.06
Nodes (23): app(), client(), signed(), test_change_webhook_rejects_a_bad_signature(), test_change_webhook_rejects_a_body_changed_after_signing(), test_change_webhook_rejects_everything_when_no_secret_is_configured(), test_change_webhook_validates_a_correctly_signed_body(), test_ingest_rejects_everything_when_no_keys_are_configured() (+15 more)

### Community 47 - "sqlalchemy"
Cohesion: 0.08
Nodes (11): upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade(), upgrade() (+3 more)

### Community 48 - "Incident lifecycle states and transitions (section 6.4)"
Cohesion: 0.22
Nodes (8): Incident lifecycle and transitions, Runbook process and controlled taxonomy, Controlled root cause taxonomy (seven categories), Incident lifecycle states and transitions (section 6.4), Runbook form fields and process (section 6.6), Seven-state incident lifecycle, Structured runbook mandatory fields, Severity and SLA defaults (P1-P4)

### Community 49 - "change_status"
Cohesion: 0.20
Nodes (7): change_status(), StatusIn, classify(), Move, Status, TransitionError, test_every_pair_matches_the_lifecycle_table()

### Community 50 - "stack.ts"
Cohesion: 0.16
Nodes (9): compose(), email(), Message, PASSWORD, ROOT, signedIn(), sql(), @playwright/test@^1.65.1 (+1 more)

### Community 51 - "migrate"
Cohesion: 0.13
Nodes (16): environment, ALERT_EVAL_SECONDS, DATABASE_URL, DEMO_USER_PASSWORD, INGEST_API_KEYS, JWT_SECRET, MAIL_FROM, S3_ACCESS_KEY (+8 more)

### Community 52 - "oncall/page.tsx"
Cohesion: 0.19
Nodes (11): OnCallPage(), TeamRotation(), shift(), asha, ben, Undelivered(), Team, move() (+3 more)

### Community 53 - "Architecture decision records index"
Cohesion: 0.12
Nodes (16): Audit immutability and non-functional requirements, Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test), Transactional audit entry (actor, action, before/after), Audit table UPDATE/DELETE-rejecting trigger, ADR 0012: Immutable audit log, 0017. Object storage with RustFS, Consequences (+8 more)

### Community 54 - "AI layer design (section 6.7)"
Cohesion: 0.50
Nodes (3): AI layer two-tier design, AI layer design (section 6.7), AI layer (retrieval + reasoning)

### Community 55 - "api.ts"
Cohesion: 0.14
Nodes (22): Policy, PointsFigure(), Added, AttachmentView(), FileForm(), submit(), RANGES, call() (+14 more)

### Community 56 - "incident.tsx"
Cohesion: 0.14
Nodes (15): Clock(), Act, Incident(), StatusBar(), Task(), Work(), IncidentPage(), IncidentsPage() (+7 more)

### Community 57 - "InfraWatch web application (Next.js)"
Cohesion: 0.29
Nodes (7): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout, Phase 1 implementation plan, Phase 1 scope (44 P1 checks plus G10.1/G10.2/walkthrough)

### Community 58 - "infrawatch_demo_app/main.py"
Cohesion: 0.17
Nodes (13): checkout(), CheckoutResponse, create_app(), health(), post_checkout(), start_fault(), stop_fault(), FaultResponse (+5 more)

### Community 60 - "vitest"
Cohesion: 0.15
Nodes (9): @testing-library/react@^16.3.3, vitest@^5.1.0, GET(), summary, timer, version, HomePage(), @testing-library/react (+1 more)

### Community 61 - "infrawatch_api/oncall.py"
Cohesion: 0.08
Nodes (28): list_on_call(), on_call_now(), Person, RotationIn, RotationOut, rotations(), set_rotation(), TeamOnCall (+20 more)

### Community 62 - "ci-passed"
Cohesion: 0.25
Nodes (9): if, name, needs, runs-on, steps, ci-passed, steps, name (+1 more)

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
Cohesion: 0.19
Nodes (13): AlertFigure(), DraftCard(), raise(), send(), DraftsPage(), RaiseIncidentPage(), describe(), Draft (+5 more)

### Community 67 - "permits"
Cohesion: 0.07
Nodes (39): require(), check(), AccessRequestIn, ApprovalIn, approve_request(), create_user(), _create_user(), pending_requests() (+31 more)

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

### Community 72 - "test_auth.py"
Cohesion: 0.23
Nodes (7): read_access_token(), client(), test_access_token_is_accepted_until_it_expires(), test_access_token_with_another_secret_or_algorithm_is_refused(), test_app_refuses_to_start_with_a_short_secret(), test_me_needs_a_bearer_token(), test_refresh_and_logout_need_the_csrf_header()

### Community 73 - "infrawatch-api FastAPI service"
Cohesion: 0.32
Nodes (8): infrawatch-api FastAPI service, infrawatch-demo-app, Branch protection on main, ci-passed aggregate status check, ADR 0016: Continuous integration and container builds, GitHub Actions ci.yml workflow, gitleaks secret history scan, Shared python.Dockerfile

### Community 74 - "attachments.py"
Cohesion: 0.07
Nodes (22): _add(), attach_file(), attach_logs(), attach_note(), attach_snapshot(), Attachment, download_file(), list_attachments() (+14 more)

### Community 75 - "ADR 0009: WebSockets for real-time updates"
Cohesion: 0.29
Nodes (8): Bounded per-connection send queue (100 msgs), 20-second WebSocket heartbeat, Incident event sequence number, WebSocket gateway, ADR 0009: WebSockets for real-time updates, ADR 0010: Event fan-out with LISTEN/NOTIFY, Incident event log, PostgreSQL LISTEN/NOTIFY channel

### Community 76 - "timers"
Cohesion: 0.23
Nodes (12): Policy, Timer, _timer(), timers(), at(), test_a_late_acknowledgement_stays_breached(), test_a_regression_to_raised_does_not_restart_the_acknowledge_clock(), test_a_reopen_restarts_the_resolve_clock_from_raised() (+4 more)

### Community 77 - "check-incidents.sh"
Cohesion: 0.38
Nodes (9): code(), expect(), fail(), move(), post(), check-incidents.sh script, team_of(), token() (+1 more)

### Community 78 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, lint, start, test, test:coverage (+1 more)

### Community 81 - "infrawatch_demo_app/telemetry.py"
Cohesion: 0.12
Nodes (10): now(), Reporter, sign(), summarise(), test_flush_signs_changes_and_keeps_data_when_the_api_is_down(), handler(), scenario(), test_request_rate_uses_the_real_window_length() (+2 more)

### Community 82 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, echarts@^6.1.0, next@16.4.5, react@19.3.0, react-dom@19.3.0, echarts, react-dom

### Community 83 - "eslint.config.mjs"
Cohesion: 0.33
Nodes (5): eslintConfig, eslint@^9.39.5, eslint-config-next@16.4.5, eslint, eslint-config-next

### Community 84 - "check-notifications.sh"
Cohesion: 0.28
Nodes (13): addressed(), as(), code(), fail(), mail(), move(), put(), check-notifications.sh script (+5 more)

### Community 86 - "next"
Cohesion: 0.29
Nodes (7): nextConfig, metadata, RootLayout(), CurrentNav(), LINKS, NavLinks(), next

### Community 87 - "attachments.tsx"
Cohesion: 0.18
Nodes (16): AccessRequestsPage(), Decision(), approve(), reject(), Pending, ROLES, Attachments(), LogForm() (+8 more)

### Community 88 - "check-escalation.sh"
Cohesion: 0.40
Nodes (8): as(), backdate(), escalations(), fail(), raise(), check-escalation.sh script, sql(), token()

### Community 89 - "check-alerts.sh"
Cohesion: 0.44
Nodes (7): cleanup(), fail(), fault(), check-alerts.sh script, sql(), token(), wait_for()

### Community 90 - "vitest.config.mts"
Cohesion: 0.40
Nodes (4): vite-tsconfig-paths@^6.1.1, @vitejs/plugin-react@^6.2.1, vite-tsconfig-paths, @vitejs/plugin-react

### Community 91 - "mail.py"
Cohesion: 0.12
Nodes (6): message(), retry_delay(), row(), test_no_cc_header_when_nobody_is_on_call(), test_retries_back_off_from_thirty_seconds_to_an_hour(), test_the_message_carries_group_to_on_call_cc_and_a_stable_id()

### Community 95 - "infrawatch_api/main.py"
Cohesion: 0.25
Nodes (4): create_app(), health(), HealthResponse, lifespan()

### Community 96 - "check-alert-baseline.sh"
Cohesion: 0.70
Nodes (4): cleanup(), fail(), check-alert-baseline.sh script, sql()

### Community 98 - "check-attachments.sh"
Cohesion: 0.35
Nodes (9): ago(), as(), attachments(), code(), expect(), fail(), check-attachments.sh script, token() (+1 more)

### Community 103 - "runbook.tsx"
Cohesion: 0.27
Nodes (9): RunbooksPage(), CATEGORIES, Category, Runbook, RunbookFields, SearchHit, searchTerms(), termRanges() (+1 more)

### Community 104 - "migrate"
Cohesion: 0.29
Nodes (7): condition, db, command, depends_on, image, restart, migrate

### Community 106 - "faults.py"
Cohesion: 0.38
Nodes (4): FaultActiveError, Faults, test_cpu_spike_starts_burners_and_stop_ends_them(), test_only_one_fault_runs_at_a_time_and_it_expires()

### Community 107 - "check-runbooks.sh"
Cohesion: 0.31
Nodes (11): as(), code(), expect(), fail(), move(), raise(), resolve(), review() (+3 more)

### Community 108 - "auth.py"
Cohesion: 0.20
Nodes (11): check_password(), _hash_refresh(), login(), LoginRequest, logout(), Me, refresh(), _require_csrf_header() (+3 more)

### Community 112 - "current_user_id"
Cohesion: 0.34
Nodes (13): load_roles(), add_checklist_item(), add_team(), assign(), change_severity(), check_item(), Detail, ensure_open() (+5 more)

### Community 114 - "live.ts"
Cohesion: 0.15
Nodes (13): LoginPage(), submit(), ALL, backoff(), OUTAGE, RESTORED, FakeSocket, session (+5 more)

### Community 120 - "check-live.py"
Cohesion: 0.25
Nodes (7): call(), fail(), main(), change(), receive(), token(), watch()

### Community 124 - "current_user_id"
Cohesion: 0.32
Nodes (3): current_user_id(), issue_access_token(), me()

### Community 128 - "runbooks.py"
Cohesion: 0.09
Nodes (22): get_runbook(), _latest(), Review, review_runbook(), ReviewIn, RunbookIn, RunbookOut, search_runbooks() (+14 more)

### Community 129 - "publish"
Cohesion: 0.20
Nodes (3): publish(), open_incident(), notify()

### Community 131 - "runbook_approved"
Cohesion: 0.31
Nodes (5): list_incidents(), runbook_approved(), _summaries(), Summary, _summary()

## Knowledge Gaps
- **59 isolated node(s):** `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app`, `infrawatch-worker`, `infrawatch-workspace` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 496 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_subscribe()` connect `live.py` to `Hub`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Capability` (e.g. with `require()` and `approve_request()`) actually correct?**
  _`Capability` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.12857142857142856 - nodes in this community are weakly interconnected._
- **Why does `record()` connect `record` to `runbooks.py`, `publish`, `permits`, `attachments.py`, `incidents.py`, `auth.py`, `drafts.py`, `infrawatch_agent/__main__.py`, `current_user_id`, `change_status`, `infrawatch_api/oncall.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Should `InfraWatch 2.0 README overview` be split into smaller, more focused modules?**
  _Cohesion score 0.08923076923076922 - nodes in this community are weakly interconnected._
- **Why does `attach_file()` connect `attachments.py` to `current_user_id`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
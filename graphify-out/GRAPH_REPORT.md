# Graph Report - Great-Observations  (2026-11-15)

## Corpus Check
- Corpus is ~24,827 words - fits in a single context window. You may not need a graph.

## Summary
- 357 nodes · 414 edges · 42 communities (20 shown, 22 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.89)
- Token cost: 222,340 input · 0 output

## Community Hubs (Navigation)
- Web Build Config
- Phase 1 Delivery
- Product Specification Core
- Agent Skeleton
- Outbox and Workers
- TypeScript Compiler Options
- API Health Endpoint
- Docker Build Inputs
- Authentication
- CI Python Job Steps
- CI Docker Matrix
- Workflow Permissions
- Next.js App Shell
- API CLI Entrypoint
- CI Workflow Header
- CI Web Job
- Dashboards and Web UI
- CI Pass Gate
- CI Triggers
- Secrets Scan Env
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

## God Nodes (most connected - your core abstractions)
1. `InfraWatch 2.0 README overview` - 19 edges
2. `with` - 17 edges
3. `compilerOptions` - 16 edges
4. `Architecture decision records index` - 10 edges
5. `scripts` - 8 edges
6. `Contributing to InfraWatch` - 7 edges
7. `ADR 0011: Authentication and tokens` - 7 edges
8. `jobs` - 6 edges
9. `ci-passed` - 6 edges
10. `Proposed technical foundations (toolchain, persistence, queue, auth, audit)` - 6 edges

## Surprising Connections (you probably didn't know these)
- `AI layer two-tier design` --semantically_similar_to--> `AI layer design (section 6.7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Severity and SLA defaults (P1-P4)` --semantically_similar_to--> `Incident lifecycle states and transitions (section 6.4)`  [INFERRED] [semantically similar]
  README.md → docs/specification.html
- `Market positioning and differentiators` --semantically_similar_to--> `Business case (problem, value, portfolio)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Full agreed decision register` --semantically_similar_to--> `Specification decision register`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Role/capability permission matrix` --semantically_similar_to--> `Eight roles and permission matrix`  [INFERRED] [semantically similar]
  context.md → docs/specification.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four-stage flow across all specification documents** — readme_four_stage_flow, context_four_stage_flow, docs_specification_overview [INFERRED 0.85]
- **Three-phase delivery roadmap P1/P2/P3** — readme_roadmap, context_phasing, docs_specification_phasing, docs_phase_1_plan_scope [INFERRED 0.85]
- **Server-side enforcement, degrade gracefully, configuration over code, reproducibility** — readme_architecture, context_design_principles, docs_specification_architecture [INFERRED 0.85]
- **Broker-free PostgreSQL-centric infrastructure (queue + outbox + fan-out)** — docs_adr_0008_outbox_table, docs_adr_0008_select_for_update_skip_locked, docs_adr_0010_listen_notify, docs_adr_0010_incident_event_log [EXTRACTED 1.00]
- **InfraWatch authentication credential stack** — docs_adr_0011_argon2id, docs_adr_0011_access_jwt, docs_adr_0011_refresh_token, docs_adr_0011_per_agent_api_key, docs_adr_0011_hmac_sha256 [EXTRACTED 1.00]
- **GitHub Actions CI job set** — docs_adr_0016_github_actions_workflow, docs_adr_0016_ci_passed_job, docs_adr_0016_python_dockerfile, docs_adr_0016_gitleaks_scan, docs_adr_0016_branch_protection [EXTRACTED 1.00]

## Communities (42 total, 22 thin omitted)

### Community 0 - "Web Build Config"
Cohesion: 0.05
Nodes (48): eslintConfig, dependencies, next@16.4.5, react@19.3.0, react-dom@19.3.0, devDependencies, eslint@^9.39.5, eslint-config-next@16.4.5 (+40 more)

### Community 1 - "Phase 1 Delivery"
Cohesion: 0.07
Nodes (32): Audit immutability and non-functional requirements, Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test) (+24 more)

### Community 2 - "Product Specification Core"
Cohesion: 0.06
Nodes (34): AI layer two-tier design, Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, Incident lifecycle and transitions, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks (+26 more)

### Community 3 - "Agent Skeleton"
Cohesion: 0.11
Nodes (6): main(), test_main_emits_structured_record(), main(), test_main_emits_structured_record(), main(), test_main_emits_structured_record()

### Community 4 - "Outbox and Workers"
Cohesion: 0.08
Nodes (29): infrawatch-api FastAPI service, infrawatch-demo-app, infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL, Scheduled periodic tasks, SELECT FOR UPDATE SKIP LOCKED job claim, Bounded per-connection send queue (100 msgs) (+21 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "API Health Endpoint"
Cohesion: 0.13
Nodes (3): create_app(), health(), HealthResponse

### Community 7 - "Docker Build Inputs"
Cohesion: 0.14
Nodes (14): with, build-args, cache, cache-dependency-path, cache-from, cache-to, context, enable-cache (+6 more)

### Community 8 - "Authentication"
Cohesion: 0.18
Nodes (12): infrawatch-agent package, Short-lived access JWT (15 min), Argon2id password hashing, ADR 0011: Authentication and tokens, HMAC-SHA256 webhook signatures, Per-agent API key, Rotating revocable refresh token, Delivery retry with exponential backoff (1-60s, jitter) (+4 more)

### Community 9 - "CI Python Job Steps"
Cohesion: 0.29
Nodes (10): steps, steps, python, name, runs-on, steps, name, run (+2 more)

### Community 10 - "CI Docker Matrix"
Cohesion: 0.20
Nodes (10): name, runs-on, strategy, build-args, file, service, docker, include (+2 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.25
Nodes (8): secrets, permissions, contents, pull-requests, name, permissions, runs-on, steps

### Community 12 - "Next.js App Shell"
Cohesion: 0.29
Nodes (3): nextConfig, metadata, next

### Community 14 - "CI Workflow Header"
Cohesion: 0.33
Nodes (5): concurrency, cancel-in-progress, group, jobs, name

### Community 15 - "CI Web Job"
Cohesion: 0.33
Nodes (6): run, web, working-directory, defaults, name, runs-on

### Community 16 - "Dashboards and Web UI"
Cohesion: 0.40
Nodes (5): Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), ADR 0014: Defer full dashboard builder to Phase 3, Prebuilt health dashboard per service (Phase 1), Simple panel builder with persistent layout

### Community 17 - "CI Pass Gate"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, ci-passed

### Community 18 - "CI Triggers"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 19 - "Secrets Scan Env"
Cohesion: 0.50
Nodes (4): GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, env

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

## Knowledge Gaps
- **61 isolated node(s):** `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app`, `infrawatch-worker`, `infrawatch-core` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 166 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Phase 1 Delivery`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Web Build Config` be split into smaller, more focused modules?**
  _Cohesion score 0.05224963715529753 - nodes in this community are weakly interconnected._
- **Why does `jobs` connect `CI Workflow Header` to `CI Python Job Steps`, `CI Docker Matrix`, `Workflow Permissions`, `CI Web Job`, `CI Pass Gate`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `Phase 1 Delivery` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Why does `Architecture decision records index` connect `Phase 1 Delivery` to `Product Specification Core`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `Product Specification Core` be split into smaller, more focused modules?**
  _Cohesion score 0.06306306306306306 - nodes in this community are weakly interconnected._
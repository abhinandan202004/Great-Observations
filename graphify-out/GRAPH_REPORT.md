# Graph Report - Great-Observations  (2026-11-16)

## Corpus Check
- 76 files · ~26,763 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 8, .typed 5, .example 1)

## Summary
- 507 nodes · 657 edges · 43 communities (21 shown, 22 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.89)
- Token cost: 222,340 input · 0 output

## Graph Freshness
- Built from commit: `36806c63`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Web Build Config
- Phase 1 Delivery
- Product Specification Core
- test_agent_entrypoint.py
- Outbox and Workers
- TypeScript Compiler Options
- API Health Endpoint
- Docker Build Inputs
- services
- args
- CI Docker Matrix
- Workflow Permissions
- compose.yaml
- seed.py
- jobs
- CI Web Job
- scripts
- environment
- CI Triggers
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

## God Nodes (most connected - your core abstractions)
1. `Architecture decision records index` - 20 edges
2. `InfraWatch 2.0 README overview` - 20 edges
3. `with` - 17 edges
4. `compilerOptions` - 16 edges
5. `Phase 1 implementation plan` - 11 edges
6. `services` - 10 edges
7. `Contributing to InfraWatch` - 9 edges
8. `scripts` - 8 edges
9. `test` - 8 edges
10. `interval` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Audit immutability and non-functional requirements` --semantically_similar_to--> `Audit (section 6.9)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Audit immutability and non-functional requirements` --semantically_similar_to--> `Non-functional requirements (section 8)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket)` --semantically_similar_to--> `Decisions confirmed on 2026-11-09`  [INFERRED] [semantically similar]
  context.md → docs/phase-1-plan.md
- `AI layer two-tier design` --semantically_similar_to--> `AI layer design (section 6.7)`  [INFERRED] [semantically similar]
  context.md → docs/specification.html
- `Compose architecture and principal data entities` --semantically_similar_to--> `Compose architecture and principal data entities (section 7)`  [INFERRED] [semantically similar]
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

## Communities (43 total, 22 thin omitted)

### Community 0 - "Web Build Config"
Cohesion: 0.05
Nodes (44): eslintConfig, nextConfig, dependencies, next@16.4.5, react@19.3.0, react-dom@19.3.0, devDependencies, eslint@^9.39.5 (+36 more)

### Community 1 - "Phase 1 Delivery"
Cohesion: 0.06
Nodes (37): Audit immutability and non-functional requirements, Items resolved on 2026-11-09 (G6.3 target, G9.1 coverage, demo teams, agent, WebSocket), Protect main branch ruleset (ci-passed check), Container image builds for api/worker/agent/demo/web, Contributing to InfraWatch, Development prerequisites (uv, Node 22, Docker 27, Git), Python CI checks (ruff, mypy, pytest), Web CI checks (npm lint, typecheck, test) (+29 more)

### Community 2 - "Product Specification Core"
Cohesion: 0.06
Nodes (34): AI layer two-tier design, Compose architecture and principal data entities, Full agreed decision register, Four-stage flow original description, Incident lifecycle and transitions, InfraWatch 2.0 project context, Role/capability permission matrix, Phasing P1/P2/P3 and acceptance checks (+26 more)

### Community 3 - "test_agent_entrypoint.py"
Cohesion: 0.09
Nodes (9): HealthHandler, base_url(), test_health_reports_ok(), test_unknown_path_is_not_found(), upgrade(), HealthHandler, base_url(), test_health_reports_ok() (+1 more)

### Community 4 - "Outbox and Workers"
Cohesion: 0.05
Nodes (45): infrawatch-agent package, infrawatch-api FastAPI service, infrawatch-demo-app, Next.js agent rules (AGENTS.md), InfraWatch web application (Next.js), infrawatch-worker package, Outbox idempotency key, ADR 0008: Job queue and transactional outbox in PostgreSQL (+37 more)

### Community 5 - "TypeScript Compiler Options"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "API Health Endpoint"
Cohesion: 0.08
Nodes (6): create_app(), health(), HealthResponse, create_app(), health(), HealthResponse

### Community 7 - "Docker Build Inputs"
Cohesion: 0.14
Nodes (14): with, build-args, cache, cache-dependency-path, cache-from, cache-to, context, enable-cache (+6 more)

### Community 8 - "services"
Cohesion: 0.09
Nodes (37): healthcheck, image, healthcheck, environment, healthcheck, image, volumes, healthcheck (+29 more)

### Community 9 - "args"
Cohesion: 0.10
Nodes (28): build, build, depends_on, environment, image, ports, MODULE, PACKAGE (+20 more)

### Community 10 - "CI Docker Matrix"
Cohesion: 0.18
Nodes (11): name, runs-on, steps, strategy, build-args, file, service, docker (+3 more)

### Community 11 - "Workflow Permissions"
Cohesion: 0.29
Nodes (7): secrets, permissions, contents, pull-requests, name, permissions, runs-on

### Community 12 - "compose.yaml"
Cohesion: 0.15
Nodes (12): name, volumes, db-data, objectstore-data, x-api-build, context, dockerfile, x-python-health (+4 more)

### Community 13 - "seed.py"
Cohesion: 0.07
Nodes (10): main(), main(), run_migrations(), DemoService, DemoUser, main(), seed(), test_every_role_has_exactly_one_demo_user() (+2 more)

### Community 14 - "jobs"
Cohesion: 0.14
Nodes (13): if, name, needs, runs-on, concurrency, cancel-in-progress, group, jobs (+5 more)

### Community 15 - "CI Web Job"
Cohesion: 0.22
Nodes (11): steps, run, web, steps, working-directory, name, run, defaults (+3 more)

### Community 16 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:coverage, typecheck

### Community 17 - "environment"
Cohesion: 0.33
Nodes (6): RUSTFS_ACCESS_KEY, RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, RUSTFS_SECRET_KEY, environment

### Community 18 - "CI Triggers"
Cohesion: 0.40
Nodes (5): on, pull_request, push, branches, branches

### Community 19 - "steps"
Cohesion: 0.18
Nodes (11): name, runs-on, steps, GITHUB_TOKEN, GITLEAKS_ENABLE_COMMENTS, RESULTS, compose-smoke, steps (+3 more)

### Community 21 - "Alerting Milestones"
Cohesion: 0.67
Nodes (3): M5 Static alerts and drafts, M9 Anomaly detection and dashboards, Gate G2 Dashboards and alerting (6 checks)

## Knowledge Gaps
- **60 isolated node(s):** `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app`, `infrawatch-worker`, `infrawatch-core` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 224 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture decision records index` connect `Phase 1 Delivery` to `Product Specification Core`, `Outbox and Workers`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **What connects `infrawatch-agent`, `infrawatch-api`, `infrawatch-demo-app` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Web Build Config` be split into smaller, more focused modules?**
  _Cohesion score 0.052525252525252523 - nodes in this community are weakly interconnected._
- **Why does `InfraWatch 2.0 README overview` connect `Product Specification Core` to `Phase 1 Delivery`, `Outbox and Workers`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Phase 1 Delivery` be split into smaller, more focused modules?**
  _Cohesion score 0.06236786469344609 - nodes in this community are weakly interconnected._
- **Why does `services` connect `services` to `args`, `compose.yaml`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `Product Specification Core` be split into smaller, more focused modules?**
  _Cohesion score 0.059379217273954114 - nodes in this community are weakly interconnected._
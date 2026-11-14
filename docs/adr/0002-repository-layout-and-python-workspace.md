# 0002. Repository layout and Python workspace

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The system consists of five deployable applications (API, worker, collector agent, demo application, web interface) developed by one person, with shared domain logic between the API and the worker. A single repository keeps changes atomic across services and allows one CI pipeline. The planned layout in the specification places every application under `apps/` but has no location for code shared between Python services.

## Decision

- One repository with deployable applications under `apps/` (`api`, `worker`, `agent`, `demo-app`, `web`), deployment configuration under `deploy/`, documentation under `docs/`, operational scripts under `scripts/` and end-to-end tests under `tests/e2e/`.
- A new top-level `packages/` directory holds libraries that are not deployed on their own. The first is `packages/core` (`infrawatch-core`), the pure domain logic described in [ADR 0003](0003-pure-domain-core.md).
- The Python projects form a single uv workspace defined in the root `pyproject.toml`, with one lock file (`uv.lock`) so that every service resolves identical dependency versions.
- Each Python project uses the `src/` layout and keeps its tests beside it in a `tests/` directory.
- The web application is a separate npm project with its own lock file; it does not participate in the Python workspace.

## Consequences

- Shared logic is imported rather than copied, and a change to it is tested against all consumers in one CI run.
- The `packages/` directory is an addition to the layout proposed in the specification; the README layout is updated accordingly.
- One lock file means a dependency upgrade affects every Python service at once, which is intended at this scale.

# 0016. Continuous integration and container builds

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

Acceptance check G9.4 requires GitHub Actions to run lint, type checks, tests and Docker builds on every push, and requires a failing check to block merging to `main`. Design principle 4 requires the system to be reproducible from a clean clone.

## Decision

- A single workflow, `.github/workflows/ci.yml`, runs on every push and pull request, with these jobs:
  - **python:** `uv sync --frozen`, Ruff lint and format check, mypy (strict) per workspace member, and pytest with branch coverage.
  - **web:** `npm ci`, ESLint, TypeScript type check (after `next typegen`) and Vitest.
  - **docker:** builds the image of every service.
  - **secrets:** scans the full history with gitleaks.
  - **ci-passed:** an aggregate job that succeeds only if every other job succeeded. It is the single required status check in branch protection, so that adding a job never requires a settings change.
- The Python services share one Dockerfile, `deploy/docker/python.Dockerfile`, parameterised by the workspace package and the module to run. It installs from the lock file with `uv sync --frozen --no-dev --no-editable` and runs as a non-root user.
- The web image uses the Next.js standalone output and runs as a non-root user.
- Base images and tool images are pinned to exact versions.
- Branch protection on `main` requires the `ci-passed` check and a pull request before merging. It is configured in the GitHub repository settings by the owner, as described in `CONTRIBUTING.md`.

## Consequences

- Every service image is built and checked on every change, so a broken Dockerfile is caught before release.
- Pinned versions make builds reproducible, at the cost of deliberate, periodic upgrades.
- Branch protection is a repository setting, not code, so it is documented and has to be verified by hand.

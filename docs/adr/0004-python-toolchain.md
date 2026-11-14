# 0004. Python toolchain

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The backend is written in Python with FastAPI. The project needs reproducible dependency resolution from a clean clone (design principle 4), fast feedback in CI, and static typing strong enough to support the correctness claims of the core logic.

## Decision

- **Python 3.12** is the target runtime for every service and for CI, pinned in `.python-version` and in each package's `requires-python`. Developers who have a different interpreter installed use the Python 3.12 build that uv downloads and manages.
- **uv** manages the workspace, the lock file and virtual environments. CI installs with `uv sync --frozen`, so an out-of-date lock file fails the build.
- **Ruff** performs linting and formatting, including the flake8-bandit security rules.
- **mypy** runs in strict mode on all Python code. It is invoked once per workspace member so that the test modules of different packages do not collide.
- **pytest** with **pytest-cov** runs the tests, using the `importlib` import mode; branch coverage is collected for every package.

## Consequences

- Ruff and uv are fast enough that the full Python check suite runs in seconds locally.
- Strict typing from the first commit avoids a later, costly typing migration.
- uv is an additional tool for contributors to install; the contributing guide documents it.

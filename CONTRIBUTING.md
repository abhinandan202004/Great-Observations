# Contributing to InfraWatch

This guide describes how to set up a development environment, run the checks that CI enforces, and propose changes.

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Git | 2.40 or later | Version control |
| [uv](https://docs.astral.sh/uv/) | 0.13.7 | Python workspace, dependencies and interpreter management |
| Node.js | 22.19 or later (22.x) | Web application |
| Docker | Engine 27 or later, with Compose v2 | Container builds and, from milestone M1, the local stack |

uv downloads and manages Python 3.12 automatically; a system-wide Python 3.12 installation is not required.

## Setting up

```bash
git clone https://github.com/abhinandan202004/Great-Observations.git
cd Great-Observations
uv sync --all-packages          # Python workspace and development tools
npm ci --prefix apps/web        # Web application dependencies
```

## Running the checks locally

CI runs exactly these checks; running them before pushing avoids failed builds.

**Python** (from the repository root):

```bash
uv run ruff check .
uv run ruff format --check .
for member in packages/core apps/api apps/worker apps/agent apps/demo-app; do uv run mypy "$member"; done
uv run pytest --cov
```

**Web** (from `apps/web`):

```bash
npm run lint
npm run typecheck
npm test
```

**Container images** (from the repository root):

```bash
docker build -f deploy/docker/python.Dockerfile --build-arg PACKAGE=infrawatch-api --build-arg MODULE=infrawatch_api -t infrawatch-api .
docker build -f apps/web/Dockerfile -t infrawatch-web .
```

The worker, agent and demo application images are built the same way as the API image, with `PACKAGE` and `MODULE` set to `infrawatch-worker` / `infrawatch_worker`, `infrawatch-agent` / `infrawatch_agent`, and `infrawatch-demo-app` / `infrawatch_demo_app`.

## Working practices

- **Branches and pull requests.** Work on a feature branch and open a pull request against `main`. Direct pushes to `main` are blocked once branch protection is enabled.
- **Commit messages.** Use the imperative mood and a concise summary line of at most 72 characters, for example `Add incident state machine`. Explain the reason for the change in the body where it is not obvious.
- **Server-side enforcement.** State transitions, permissions, mandatory fields and closure rules are enforced in the API. The user interface is presentation only.
- **Domain logic.** Rules belong in `packages/core`, which performs no I/O ([ADR 0003](docs/adr/0003-pure-domain-core.md)).
- **Decisions.** Record each significant decision as an ADR in `docs/adr/` ([ADR 0001](docs/adr/0001-record-architecture-decisions.md)).
- **Secrets.** Never commit secrets. Configuration is supplied through `.env`, which is ignored by Git; `.env.example` documents every variable with a safe placeholder.
- **Honest documentation.** Mark features that are not yet built as planned. Any figure quoted in documentation must be reproducible by a script in `scripts/`.
- **Acceptance checks.** Mark a check in the specification as passed only after it has been verified.

## Branch protection (repository owner)

Acceptance check G9.4 requires that a failing check blocks merging to `main`. The workflow in `.github/workflows/ci.yml` provides the checks; blocking the merge is a repository setting that the owner applies once:

1. Push the branch containing `.github/workflows/ci.yml` and let the workflow run once, so that GitHub knows the `ci-passed` check.
2. In the repository on GitHub, open **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
3. Set **Ruleset name** to `Protect main`, **Enforcement status** to *Active*, and under **Target branches** add the **default branch**.
4. Enable the following rules:
   - **Restrict deletions**
   - **Block force pushes**
   - **Require a pull request before merging** (required approvals may be left at 0 for a single maintainer)
   - **Require status checks to pass**, with **Require branches to be up to date before merging** selected, and add the status check **`ci-passed`**.
5. Save the ruleset.

To verify, open a pull request that introduces a deliberate lint error: the `ci-passed` check fails, and the merge button stays disabled until the error is fixed.

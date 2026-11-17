# InfraWatch web application

Next.js (App Router, TypeScript) user interface for InfraWatch: dashboards, incident views, the runbook editor and administration.

> **Status:** telemetry charts and log search (milestone M2). Incident views follow in later milestones; see [`docs/phase-1-plan.md`](../../docs/phase-1-plan.md).

## Pages

| Page | Shows |
|---|---|
| `/telemetry` | One chart per metric of the chosen service, refreshed every 5 s, with deploy, config and feature-flag events as vertical markers and in a table |
| `/logs` | Log search by service, level, time range and text or correlation ID |

The browser calls the API through `/api/*`, which the web server forwards to `API_URL` (default `http://localhost:8000`; the container image is built with `http://api:8000`). `API_URL` is read at build time.

## Commands

Run from this directory after `npm ci`.

| Command | Purpose |
|---|---|
| `npm run dev` | Start the development server on `http://localhost:3000` |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Run the TypeScript compiler without emitting output |
| `npm test` | Run unit tests with Vitest |
| `npm run test:coverage` | Run unit tests with a coverage report |
| `npm run build` | Produce a production build (standalone output) |

## Container image

The image is built from the repository root:

```bash
docker build -f apps/web/Dockerfile -t infrawatch-web .
```

## Note on `AGENTS.md`

`AGENTS.md` is generated and maintained by `next dev`. It is committed so that the working tree stays clean after running the development server.

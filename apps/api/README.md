# infrawatch-api

FastAPI service providing authentication and RBAC, telemetry ingest endpoints, the incident and workflow API, the WebSocket gateway and audit writing.

> **Status:** application skeleton with a health endpoint only (milestone M0). Functional endpoints are delivered from milestone M1 onward; see [`docs/phase-1-plan.md`](../../docs/phase-1-plan.md).

## Running locally

From the repository root:

```bash
uv run --package infrawatch-api infrawatch-api
```

The service listens on `http://localhost:8000`; interactive documentation is at `/docs`.

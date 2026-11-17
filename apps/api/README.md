# infrawatch-api

FastAPI service providing authentication and RBAC, telemetry ingest endpoints, the incident and workflow API, the WebSocket gateway and audit writing.

> **Status:** telemetry ingest and queries (milestone M2). Authentication, incidents and the rest follow; see [`docs/phase-1-plan.md`](../../docs/phase-1-plan.md).

## Telemetry ingest

| Endpoint | Authentication | Body |
|---|---|---|
| `POST /ingest/metrics` | `Authorization: Bearer <ingest key>` | `{service, samples: [{time, metric, value}]}` |
| `POST /ingest/logs` | `Authorization: Bearer <ingest key>` | `{service, entries: [{id, time, level, message, correlation_id}]}` |
| `POST /ingest/changes` | HMAC signature (below) | `{id, time, service, kind, summary}` |

Ingest keys come from `INGEST_API_KEYS` (comma-separated). Times must carry a time zone. Batches hold at most 1,000 items. Sending the same batch or event twice stores it once, so senders can safely retry.

### Change-event webhook

A CI/CD or configuration system reports deploys, config changes and feature-flag changes (`kind`: `deploy`, `config` or `feature_flag`). It signs the exact request body with HMAC-SHA256 using `CHANGE_WEBHOOK_SECRET` and sends the hex digest in a header:

```bash
body='{"id":"<new uuid>","time":"2026-11-16T10:00:00Z","service":"checkout","kind":"deploy","summary":"Deployed v2.4.1"}'
signature="sha256=$(printf '%s' "$body" | openssl dgst -sha256 -hmac "$CHANGE_WEBHOOK_SECRET" | sed 's/^.* //')"
curl -X POST http://localhost:8000/ingest/changes   -H "X-Signature-256: $signature" -H "Content-Type: application/json" -d "$body"
```

A missing or wrong signature gets `401`. The `id` is chosen by the sender and makes a replayed request harmless.

## Telemetry queries

These are open until M3 puts every read endpoint behind login.

| Endpoint | Returns |
|---|---|
| `GET /services` | Service names |
| `GET /services/{service}/metrics?since=` | Names of the metrics reported since then |
| `GET /services/{service}/metrics/{metric}?since=` | Samples, oldest first (newest 2,000) |
| `GET /services/{service}/changes?since=` | Deploy, config and feature-flag events, oldest first (newest 500) |
| `GET /logs?since=&until=&service=&level=&q=&limit=` | Log entries, newest first (200 by default, 1,000 at most) |

`since` is required and, like `until`, must carry a time zone. `q` matches words in the message (English full-text search) or an exact correlation ID.

## Running locally

From the repository root:

```bash
uv run --package infrawatch-api infrawatch-api
```

The service listens on `http://localhost:8000`; interactive documentation is at `/docs`.

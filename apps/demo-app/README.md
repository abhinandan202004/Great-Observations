# infrawatch-demo-app

A simulated `checkout` service that gives InfraWatch something to observe. A background loop sends about 5 checkout requests a second; each one calls a simulated `payment-gateway`.

## What it reports

Every 5 seconds it posts to the ingest API, as the service `checkout`:

- **Metrics:** `request_rate_per_s`, `error_rate_percent` and `latency_p95_ms` for the window just ended. An empty window reports no latency.
- **Logs:** one structured entry per request with a level (`info`, `warning` for slow calls, `error` for failures) and a **correlation id**.
- **Change events:** signed with HMAC-SHA256 (see the [API README](../api/README.md)).

Unsent data waits in bounded in-memory queues (about 28 minutes of metrics, 3 minutes of logs) and is retried with the next window. It does not survive a restart of the demo app.

## Fault injection (G1.6)

```bash
docker compose exec demo-app python -m infrawatch_demo_app.fault error-burst
docker compose exec demo-app python -m infrawatch_demo_app.fault cpu-spike --minutes 2
docker compose exec demo-app python -m infrawatch_demo_app.fault stop
```

| Fault | Effect | Shows up as |
|---|---|---|
| `cpu-spike` | Busy processes on every core, at low priority | `cpu_percent` of `demo-host` near 100 |
| `error-burst` | Half of all checkouts fail | `error_rate_percent` near 50, `error` logs |
| `bad-deploy` | Emits a deploy change event, then 30% errors and slower calls | A deploy marker, then errors and latency |
| `dependency-latency` | The payment-gateway call takes 0.8 s longer | `latency_p95_ms` above 800, `warning` logs |

A fault stops by itself after `--minutes` (default 5, at most 60). Only one runs at a time; starting a second is refused until the first is stopped. The fault endpoints have no authentication: Compose publishes the demo app on `127.0.0.1` only.

# infrawatch-agent

InfraWatch collector agent: reports host metrics to the ingest API with a bounded on-disk buffer ([ADR 0015](../../docs/adr/0015-python-collector-agent.md)).

## What it reports

Every `AGENT_INTERVAL_SECONDS` (default 5) it records `cpu_percent`, `memory_percent`, `disk_percent` (of `/`), `net_sent_bytes_per_s`, `net_recv_bytes_per_s` and `agent_samples_dropped` for the service named by `AGENT_SERVICE` (default `demo-host`), and posts them to `INGEST_URL` with the bearer key `INGEST_API_KEY`.

In Compose the agent runs in its own container, so CPU, memory and disk describe the Docker host (the Docker Desktop VM on Windows and macOS), while network rates describe the agent container's own interface.

## Buffer and retry (G1.5)

- Unsent samples are kept in SQLite at `AGENT_BUFFER_PATH` (in Compose, the `agent-buffer` volume), committed on every write, so a restart, a crash or an API outage loses nothing that was already buffered.
- The buffer holds at most **10,000 samples: about 2 hours 20 minutes** at the default interval. When it is full the **oldest** samples are dropped, and the number dropped is reported in the next reading as `agent_samples_dropped`.
- Failed deliveries are retried with exponential backoff from 1 s to 60 s with jitter. A batch the API rejects as malformed (HTTP 422) is dropped and logged, so it cannot block the queue; every other failure is retried.
- `docker compose down --volumes` deletes the buffer along with the rest of the stack's data.

`scripts/check-telemetry.sh` checks this end to end against the Compose stack.

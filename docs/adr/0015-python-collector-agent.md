# 0015. Python collector agent with a bounded on-disk buffer

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The platform uses its own collector agent rather than an existing one. The agent must report CPU, memory, disk and network metrics visibly within 15 seconds (G1.1), and must tolerate a restart or network loss without losing data beyond a documented buffer (G1.5). Python, Go and Rust were considered. Go and Rust produce smaller, single-binary agents; Python shares the toolchain and ingest schemas with the API.

## Decision

- The agent is written in **Python** using `psutil` for host metrics and `httpx` for delivery, as the `infrawatch-agent` workspace package.
- It reports every **5 seconds** by default (configurable).
- Unsent samples are held in an **on-disk SQLite queue** of at most **10,000 samples** (approximately 15 minutes at the default interval and metric set), so they survive an agent restart.
- When the buffer is full, the **oldest samples are dropped**, and the number of dropped samples is reported as a metric so that loss is visible rather than silent.
- Delivery retries use **exponential backoff from 1 second to 60 seconds with jitter**.
- The agent authenticates with a per-agent API key ([ADR 0011](0011-authentication-and-tokens.md)).

## Consequences

- One language and one CI toolchain for all backend components, and shared request schemas with the ingest API.
- The agent has a larger runtime footprint than a compiled binary would, which is acceptable for a demonstration deployment; a compiled agent remains a possible later replacement behind the same ingest API.

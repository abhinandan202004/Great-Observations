# 0009. WebSockets for real-time updates

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

Incident pages must update live for all open viewers and recover after a dropped connection (G3.9). Server-sent events were considered and would have been sufficient for one-way updates; WebSockets were chosen during requirements analysis. WebSockets require the application to define its own resumption and flow-control behaviour.

## Decision

- The API exposes a WebSocket gateway. Clients authenticate when the connection opens and subscribe to the incidents they view.
- Every incident event carries a sequence number that increases monotonically per incident.
- On reconnection, with exponential backoff, the client sends the last sequence number it processed. The server replays the missed events from the incident event log. If the gap is larger than the replay window, the server instructs the client to fetch the full incident again.
- Each connection has a bounded send queue of 100 messages. If a slow client overflows it, the server closes the connection with a "resync required" close code, and the client reconnects and refetches.
- A heartbeat is exchanged every 20 seconds so that dead connections are detected.
- The WebSocket channel carries notifications only. All changes are made through the REST API, where permissions are enforced.

## Consequences

- Viewers see a consistent sequence of events with no silent gaps.
- A slow client cannot consume unbounded server memory.
- The behaviour is more complex than server-sent events and is covered by a dedicated connection-drop test in milestone M8.

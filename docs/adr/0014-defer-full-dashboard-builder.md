# 0014. Defer the full dashboard builder to Phase 3

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

A full Grafana-style dashboard builder (query editor, variables, many panel types) was requested. It is a large piece of work that competes for effort with the incident and AI loop, which is where the project's differentiators lie.

## Decision

- Phase 1 delivers a prebuilt health dashboard for each registered service and a simple panel builder that can add, remove and rearrange basic metric panels, with a persistent layout (G2.1, G2.2).
- The full builder is scheduled for Phase 3.

## Consequences

- Phase 1 effort stays on the end-to-end incident workflow.
- The panel and layout model introduced in Phase 1 should be designed so that the Phase 3 builder can extend it rather than replace it.

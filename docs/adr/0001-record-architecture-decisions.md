# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

InfraWatch 2.0 is developed against a detailed specification, and acceptance check G10.2 requires an architecture decision record for each major decision. Decisions made in conversation or in commit messages are hard to find later and easy to contradict unknowingly.

## Decision

Each significant decision is recorded as a short Markdown file in `docs/adr/`, numbered sequentially, with the sections Context, Decision and Consequences, and a status of Proposed, Accepted or Superseded. Records are not edited after acceptance except to change their status; a revised decision is written as a new record that supersedes the old one. The index in `docs/adr/README.md` is kept current.

## Consequences

- Reviewers and future contributors can trace why the system is shaped as it is.
- Writing a record adds a small cost to each significant change, which is accepted.

# 0011. Authentication and tokens

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The system uses local accounts with role-based access control. Acceptance check G8.2 requires hashed passwords and expiring tokens, and G8.1 requires every endpoint to enforce permissions on the server.

## Decision

- Passwords are hashed with **Argon2id**.
- A successful login issues a short-lived **access JWT** (15 minutes) and a **refresh token** that is rotated on every use and stored server-side, so that it can be revoked.
- The signing key is supplied through the environment and is never committed; `.env.example` contains a placeholder only.
- Every endpoint declares its required permission, which is evaluated by the permission policy in `infrawatch-core` using the caller's roles and team memberships. The user interface hides controls a user cannot use, but hiding is never the enforcement mechanism.
- Telemetry ingest uses per-agent API keys, and the change-event webhook uses HMAC-SHA256 request signatures. These machine credentials are separate from user tokens.

## Consequences

- A stolen access token is useful for at most 15 minutes, and a refresh token can be revoked.
- Server-side refresh-token storage adds a table and a lookup per refresh, which is acceptable.

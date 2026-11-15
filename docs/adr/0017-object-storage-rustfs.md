# 0017. Object storage with RustFS

- **Status:** Accepted
- **Date:** 2026-11-16
- **Supersedes:** the MinIO reference in [ADR 0006](0006-database-timescaledb-and-pgvector.md)

## Context

Attachments (log excerpts, files and screenshots) need S3-compatible object storage (G4.2, G9.2). The specification named MinIO, but its repository was archived on 2026-04-25 and its container images are no longer published, so it cannot be pinned or receive security fixes.

## Decision

- **RustFS** (`rustfs/rustfs`, pinned in `compose.yaml`) provides object storage in the Compose stack, as the `objectstore` service.
- The application talks to it only through the S3 API with path-style addressing and SigV4, configured by endpoint and credentials. No RustFS-specific API is used.
- Where the specification or acceptance checks say "MinIO", RustFS fills that role; the checks themselves are unchanged.

## Consequences

- Any S3-compatible store (Silo, SeaweedFS, AWS S3) can replace RustFS by changing the image and environment, with no code change.
- RustFS is younger than MinIO; the G9.2 integration tests run against it so an incompatibility surfaces in CI rather than in the demo.

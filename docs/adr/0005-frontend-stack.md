# 0005. Frontend stack

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

The web interface presents dashboards with time-series charts and change markers (G1.4, G2.1), a simple panel builder with persistent layout (G2.2), incident views with live updates (G3.9) and the runbook editor. Next.js was chosen for the frontend in the requirements phase.

## Decision

- **Next.js 16** with the App Router and TypeScript in strict mode, built with `output: "standalone"` for a small container image.
- **Apache ECharts** for time-series charts, because it renders large series efficiently and supports chart markers natively, which suits change-event markers.
- **react-grid-layout** for the simple panel builder (add, remove, rearrange), without a custom layout engine.
- **Vitest** with React Testing Library for unit tests, and **Playwright** for end-to-end tests.
- **ESLint** with the Next.js configuration. ESLint remains on major version 9 because several plugins bundled with `eslint-config-next` 16.4 do not yet declare support for version 10.
- No web fonts are fetched at build time; the interface uses the system font stack, so builds do not depend on external font services.

## Consequences

- One framework covers server rendering, routing and the API client.
- ECharts and react-grid-layout are added when the dashboard milestones begin, not before.
- The ESLint major version should be revisited once the Next.js configuration supports version 10.

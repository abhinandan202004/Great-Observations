# infrawatch-worker

InfraWatch worker: alert evaluation, anomaly detection, SLA timers, escalation, email dispatch and scheduled jobs.

> **Status:** serves `/health` (M1) and evaluates the static alert rules every `ALERT_EVAL_SECONDS` (default 15), turning a breach that lasts a rule's duration into a draft for Production Support (M5). SLA, escalation and email jobs follow; see [`docs/phase-1-plan.md`](../../docs/phase-1-plan.md).

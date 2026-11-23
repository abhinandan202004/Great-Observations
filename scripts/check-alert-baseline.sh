#!/usr/bin/env bash
# G2.3 (no false firing): with no fault running, the seeded alert rules stay quiet over a normal
# baseline. A canary rule that always fires proves the worker evaluated rules for the whole run.
#
#   bash scripts/check-alert-baseline.sh            # 30 minutes, the G2.3 run
#   bash scripts/check-alert-baseline.sh 5          # a shorter trial
#
# Do not build images or run other load on the host meanwhile: host CPU is one of the rules.
set -euo pipefail

minutes=${1:-30}
sql() { docker compose exec -T db psql -U postgres -d infrawatch -qtAc "$1"; }
fail() { echo "::error::$1"; exit 1; }

docker compose exec -T demo-app python -m infrawatch_demo_app.fault stop >/dev/null
canary=$(sql "INSERT INTO alert_rules (name, service_id, metric, comparator, threshold,
  duration_seconds, severity) SELECT 'baseline canary $(date +%s)', id, 'request_rate_per_s',
  'above', -1, 0, 'P4' FROM services WHERE name = 'checkout' RETURNING id")
cleanup() { # the canary's draft is not for Production Support
  sql "UPDATE alert_rules SET enabled = false WHERE id = '${canary}';
    UPDATE alerts SET state = 'dismissed', decided_at = now() WHERE rule_id = '${canary}'"
}
trap cleanup EXIT
started=$(sql "SELECT now()")
watched=$(sql "SELECT string_agg(name, ', ') FROM alert_rules WHERE enabled AND id <> '${canary}'")

echo "Watching ${watched} for ${minutes} minutes from ${started}"
sleep $((minutes * 60))

fired=$(sql "SELECT coalesce(string_agg(r.name || ' at ' || a.last_fired_at, '; '), '')
  FROM alerts a JOIN alert_rules r ON r.id = a.rule_id
  WHERE a.last_fired_at > '${started}' AND r.id <> '${canary}'")
[ -z "${fired}" ] || fail "a rule fired on the normal baseline: ${fired}"
[ "$(sql "SELECT max(last_fired_at) > now() - interval '1 minute' FROM alerts
  WHERE rule_id = '${canary}'")" = t ] || fail "the worker stopped evaluating rules during the run"

echo "baseline: no rule fired in ${minutes} minutes of normal traffic, and the canary shows the worker evaluated throughout"

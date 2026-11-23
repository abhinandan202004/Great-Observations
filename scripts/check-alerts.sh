#!/usr/bin/env bash
# G2.3 (firing part) and G2.6 against the running stack: a static rule fires on an injected fault
# only after its duration, the firing becomes one draft holding a frozen metric snapshot, only
# Production Support raises it, and a later firing folds into the raised incident, not a new draft.
# The 30-minute no-false-firing run is scripts/check-alert-baseline.sh.
set -euo pipefail

api=http://localhost:8000
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')

fail() { echo "::error::$1"; exit 1; }
sql() { docker compose exec -T db psql -U postgres -d infrawatch -qtAc "$1"; }
fault() { docker compose exec -T demo-app python -m infrawatch_demo_app.fault "$@" >/dev/null; }
code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
token() {
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
wait_for() { # <seconds> <what> <SQL that answers t once it holds>
  for _ in $(seq "$1"); do
    [ "$(sql "$3")" = t ] && return 0
    sleep 1
  done
  fail "timed out after $1 s waiting for $2"
}

support=$(token support)
developer=$(token developer)
admin=$(token admin)

# A rule of this run's own, so earlier runs' raised incidents cannot absorb its firings.
rule=$(sql "INSERT INTO alert_rules (name, service_id, metric, comparator, threshold,
  duration_seconds, severity) SELECT 'check-alerts $(date +%s)', id, 'error_rate_percent',
  'above', 15, 30, 'P2' FROM services WHERE name = 'checkout' RETURNING id")
cleanup() {
  fault stop || true
  sql "UPDATE alert_rules SET enabled = false WHERE id = '${rule}'" || true
}
trap cleanup EXIT
alerts="FROM alerts WHERE rule_id = '${rule}'"

echo "G2.3: the rule fires on an injected error burst, once the breach has lasted 30 s"
fault stop
fault error-burst --minutes 3
wait_for 150 "the rule to fire" "SELECT EXISTS (SELECT 1 ${alerts} AND state = 'draft')"
[ "$(sql "SELECT last_fired_at - breach_started_at >= interval '30 seconds' ${alerts}")" = t ] \
  || fail "the rule fired before the breach lasted its duration"

echo "G2.6: one draft for the ongoing breach, with a frozen snapshot"
sleep 20 # at least one more evaluation while the breach continues
[ "$(sql "SELECT count(*) || '|' || max(fire_count) ${alerts}")" = "1|1" ] \
  || fail "the ongoing breach created more than one draft or counted twice"
alert=$(sql "SELECT id ${alerts}")
points=$(sql "SELECT jsonb_array_length(snapshot) ${alerts}")
[ "${points}" -gt 6 ] || fail "the snapshot holds only ${points} points"
[ "$(sql "SELECT count(*) FROM incidents i JOIN alerts a ON a.incident_id = i.id WHERE a.id = '${alert}'")" = 0 ] \
  || fail "a draft became an incident without Production Support"

echo "G2.6 and G3.1: only Production Support raises the draft"
raise='{"title":"Checkout error burst","impact":"Payments failing","description":"From the alert","severity":"P2"}'
[ "$(code -H "Authorization: Bearer ${developer}" "${json[@]}" -d "${raise}" "${api}/drafts/${alert}/raise")" = 403 ] \
  || fail "a developer raised a draft"
incident=$(curl -fsS -H "Authorization: Bearer ${support}" "${json[@]}" -d "${raise}" \
  "${api}/drafts/${alert}/raise" | sed -E 's/^\{"id":"([^"]+)".*/\1/')
curl -fsS -H "Authorization: Bearer ${support}" "${api}/drafts" | grep -q "${alert}" \
  && fail "a raised draft is still listed as a draft"
[ "$(code -H "Authorization: Bearer ${support}" "${json[@]}" -d "${raise}" "${api}/drafts/${alert}/raise")" = 404 ] \
  || fail "a draft was raised twice"

echo "Deduplication: a second breach folds into the raised incident"
fault stop
wait_for 60 "the error rate to return to normal" "SELECT value < 15 FROM metric_samples m
  JOIN services s ON s.id = m.service_id WHERE s.name = 'checkout'
  AND metric = 'error_rate_percent' ORDER BY time DESC LIMIT 1"
fault error-burst --minutes 3
wait_for 150 "the second breach to fold into the incident" "SELECT fire_count = 2 ${alerts} AND id = '${alert}'"
[ "$(sql "SELECT count(*) ${alerts}")" = 1 ] || fail "the second breach created a new draft"
[ "$(sql "SELECT jsonb_array_length(snapshot) ${alerts}")" = "${points}" ] || fail "the snapshot changed"
curl -fsS -H "Authorization: Bearer ${developer}" "${api}/incidents/${incident}" \
  | grep -q '"fire_count":2,"snapshot":\[{"time"' || fail "the incident does not show the alert and its snapshot"

echo "Rules: only the admin changes them"
update='{"threshold":15,"duration_seconds":30,"severity":"P2","enabled":false}'
[ "$(code -X PUT -H "Authorization: Bearer ${developer}" "${json[@]}" -d "${update}" "${api}/alert-rules/${rule}")" = 403 ] \
  || fail "a developer changed a rule"
[ "$(code -X PUT -H "Authorization: Bearer ${admin}" "${json[@]}" -d "${update}" "${api}/alert-rules/${rule}")" = 200 ] \
  || fail "the admin could not change a rule"

audit=$(sql "SELECT string_agg(action, ',') FROM audit_log WHERE target_id IN ('${incident}', '${rule}')")
for action in incident.raise alert_rule.update; do
  case ",${audit}," in *",${action},"*) ;; *) fail "no audit row for ${action}: ${audit}" ;; esac
done

echo "alerts: the rule fires after its duration, drafts hold a frozen snapshot, only Production Support raises them, and repeats fold in"

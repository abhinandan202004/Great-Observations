#!/usr/bin/env bash
# Checks the telemetry acceptance criteria against a running, seeded Compose stack:
#   G1.1  agent metrics are readable through the API, and the newest is at most 15 s old;
#   resending a batch stores nothing twice (the agent resends after a lost response);
#   G1.2  the demo app's request rate, error rate and latency are ingested;
#   G1.3  logs arrive with correlation ids and are searchable by service, level, time and text;
#   G1.4  signed deploy, config and feature-flag events are stored and served for the chart
#         markers, a bad signature is refused;
#   the web app serves the chart and log pages and proxies the API;
#   G1.6  each injected fault changes the telemetry within 60 s;
#   G1.5  stopping the API and restarting the agent leaves no gap in the stored samples.
set -euo pipefail

sql() { docker compose exec -T db psql -U postgres -d infrawatch -tAc "$1"; }
utc_now() { sql "SELECT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"; }
api_points_since() {
  curl -fs "http://localhost:8000/services/demo-host/metrics/cpu_percent?since=$1" | grep -o '"time"' | wc -l
}
wait_until() { # <seconds> <description> <SQL returning true>
  local deadline=$(( $(date +%s) + $1 ))
  until [ "$(sql "$3")" = t ]; do
    if [ "$(date +%s)" -ge "${deadline}" ]; then
      echo "::error::Timed out after $1 s waiting for: $2"
      return 1
    fi
    sleep 2
  done
}
metric_above() { # <service> <metric> <threshold> <since>: SQL that is true once a sample exceeds it
  echo "SELECT max(m.value) > $3 FROM metric_samples m JOIN services s ON s.id = m.service_id
        WHERE s.name = '$1' AND m.metric = '$2' AND m.time > '$4'"
}
api() { curl -fsS "http://localhost:8000$1"; }
count() { grep -o "$1" | wc -l; } # occurrences on stdin
fault() { docker compose exec -T demo-app python -m infrawatch_demo_app.fault "$@" >/dev/null; }
wait_for_points_since() {
  for _ in $(seq 1 30); do
    [ "$(api_points_since "$1")" -gt 0 ] && return 0
    sleep 3
  done
  echo "::error::No agent samples newer than $1 within 90 s" && return 1
}

echo "G1.1: waiting for agent samples through the API"
wait_for_points_since "2000-01-01T00:00:00Z"
sleep 6
age=$(sql "SELECT extract(epoch FROM now() - max(time))::int FROM metric_samples WHERE metric = 'cpu_percent'")
echo "Newest sample is ${age} s old (limit 15 s)"
[ "${age}" -le 15 ]

echo "Ingest is idempotent: a batch resent after a lost response is stored once"
key=$(docker compose exec -T agent printenv INGEST_API_KEY)
sent_at=$(utc_now)
batch="{\"service\":\"demo-host\",\"samples\":[{\"time\":\"${sent_at}\",\"metric\":\"resend_check\",\"value\":1}]}"
for _ in 1 2; do
  curl -fsS -X POST http://localhost:8000/ingest/metrics -H "Authorization: Bearer ${key}" \
    -H "Content-Type: application/json" -d "${batch}" >/dev/null
done
[ "$(sql "SELECT count(*) FROM metric_samples WHERE metric = 'resend_check' AND time = '${sent_at}'")" = 1 ]

echo "G1.2: demo-app request rate, error rate and latency arrive"
wait_until 60 "checkout request metrics" "SELECT count(DISTINCT m.metric) = 3
  FROM metric_samples m JOIN services s ON s.id = m.service_id WHERE s.name = 'checkout'
  AND m.metric IN ('request_rate_per_s', 'error_rate_percent', 'latency_p95_ms')"

echo "G1.3: logs arrive with correlation ids and are searchable by service, level, time and text"
wait_until 60 "checkout logs" "SELECT count(*) > 0 AND bool_and(correlation_id IS NOT NULL) FROM log_entries"
checks_start=$(utc_now)
all="/logs?since=2000-01-01T00:00:00Z"
found=$(api "${all}&service=checkout&level=info&q=completed&limit=5")
[ "$(echo "${found}" | count '"correlation_id":"')" -ge 1 ]
[ "$(echo "${found}" | count '"level":"info"')" = "$(echo "${found}" | count '"level"')" ]
[ "$(api "${all}&service=demo-host")" = "[]" ]
[ "$(api "${all}&until=2000-01-02T00:00:00Z")" = "[]" ]
[ "$(api "${all}&q=nosuchwordanywhere")" = "[]" ]
one_id=$(sql "SELECT correlation_id FROM log_entries LIMIT 1")
[ "$(api "${all}&q=${one_id}" | count '"correlation_id"')" = 1 ]

echo "G1.4: signed change events of every kind are stored; a bad signature is refused"
secret=$(docker compose exec -T api printenv CHANGE_WEBHOOK_SECRET)
for kind in deploy config feature_flag; do
  body="{\"id\":\"$(sql 'SELECT gen_random_uuid()')\",\"time\":\"$(utc_now)\",\"service\":\"checkout\",\"kind\":\"${kind}\",\"summary\":\"telemetry check ${kind}\"}"
  signature="sha256=$(printf '%s' "${body}" | openssl dgst -sha256 -hmac "${secret}" | sed 's/^.* //')"
  curl -fsS -X POST http://localhost:8000/ingest/changes -H "X-Signature-256: ${signature}"     -H "Content-Type: application/json" -d "${body}" >/dev/null
done
[ "$(sql "SELECT count(DISTINCT kind) FROM change_events WHERE summary LIKE 'telemetry check %'")" = 3 ]
refused=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/ingest/changes   -H "X-Signature-256: sha256=00" -H "Content-Type: application/json" -d "${body}")
[ "${refused}" = 401 ]
[ "$(api "/services/checkout/changes?since=${checks_start}" | count '"summary":"telemetry check ')" = 3 ]

echo "Web: the chart and log pages load, and the browser's API route reaches the API"
web="http://$(docker compose port web 3000)"
curl -fsS -o /dev/null "${web}/telemetry"
curl -fsS -o /dev/null "${web}/logs"
services=$(curl -fsS "${web}/api/services")
[ "${services}" = '["checkout","demo-host","payment-gateway"]' ] || { echo "::error::web app served services: ${services}"; exit 1; }
# Polls: the demo app reports every 5 s, so the metric may not exist yet at the first look.
for _ in $(seq 1 20); do
  metrics=$(curl -fsS "${web}/api/services/checkout/metrics?since=${checks_start}" || true)
  case "${metrics}" in *'"latency_p95_ms"'*) break ;; esac
  sleep 3
done
case "${metrics}" in *'"latency_p95_ms"'*) ;; *) echo "::error::web app served checkout metrics: ${metrics}"; exit 1 ;; esac

echo "G1.6: each fault changes the telemetry within 60 s"
since=$(utc_now); fault error-burst --minutes 2
wait_until 60 "error-burst to raise the error rate" "$(metric_above checkout error_rate_percent 20 "${since}")"
fault stop
since=$(utc_now); fault dependency-latency --minutes 2
wait_until 60 "dependency-latency to raise p95 latency" "$(metric_above checkout latency_p95_ms 500 "${since}")"
fault stop
since=$(utc_now); fault cpu-spike --minutes 2
wait_until 60 "cpu-spike to raise host CPU" "$(metric_above demo-host cpu_percent 80 "${since}")"
fault stop
since=$(utc_now); fault bad-deploy --minutes 2
wait_until 60 "bad-deploy to emit a deploy event" "SELECT count(*) = 1 FROM change_events
  WHERE kind = 'deploy' AND summary LIKE '%injected bad deploy%' AND time >= '${since}'"
wait_until 60 "bad-deploy to raise the error rate" "$(metric_above checkout error_rate_percent 20 "${since}")"
fault stop

echo "G1.5: API down for 30 s, agent restarted in the middle"
drill_start=$(utc_now)
docker compose stop api
sleep 15
docker compose restart agent
sleep 15
docker compose start api
drill_end=$(utc_now)
wait_for_points_since "${drill_end}"

gap=$(sql "SELECT coalesce(max(gap), 0)::int FROM (
  SELECT extract(epoch FROM time - lag(time) OVER (ORDER BY time)) AS gap
  FROM metric_samples m JOIN services s ON s.id = m.service_id
  WHERE s.name = 'demo-host' AND m.metric = 'cpu_percent'
    AND time BETWEEN '${drill_start}'::timestamptz - interval '10 seconds' AND '${drill_end}'
) gaps")
echo "Largest gap between samples across the drill: ${gap} s (limit 12 s)"
[ "${gap}" -le 12 ]

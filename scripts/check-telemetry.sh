#!/usr/bin/env bash
# Checks G1.1 and G1.5 against a running, seeded Compose stack:
#   G1.1  agent metrics are readable through the API, and the newest is at most 15 s old;
#   G1.5  stopping the API and restarting the agent leaves no gap in the stored samples.
set -euo pipefail

sql() { docker compose exec -T db psql -U postgres -d infrawatch -tAc "$1"; }
api_points_since() {
  curl -fs "http://localhost:8000/services/demo-host/metrics/cpu_percent?since=$1" | grep -o '"time"' | wc -l
}
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

echo "G1.5: API down for 30 s, agent restarted in the middle"
drill_start=$(sql "SELECT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')")
docker compose stop api
sleep 15
docker compose restart agent
sleep 15
docker compose start api
drill_end=$(sql "SELECT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')")
wait_for_points_since "${drill_end}"

gap=$(sql "SELECT coalesce(max(gap), 0)::int FROM (
  SELECT extract(epoch FROM time - lag(time) OVER (ORDER BY time)) AS gap
  FROM metric_samples m JOIN services s ON s.id = m.service_id
  WHERE s.name = 'demo-host' AND m.metric = 'cpu_percent'
    AND time BETWEEN '${drill_start}'::timestamptz - interval '10 seconds' AND '${drill_end}'
) gaps")
echo "Largest gap between samples across the drill: ${gap} s (limit 12 s)"
[ "${gap}" -le 12 ]

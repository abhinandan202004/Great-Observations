#!/usr/bin/env bash
# G4.3, G4.4, G4.5 and G4.7 against the running stack, read back from Mailpit: one email per
# event (raise, severity, new team, Resolved) to the group addresses with the on-call in CC, none
# for minor steps, the CC following the rotation, the admin told about a team with no on-call,
# and a mail outage that delays email without blocking the incident.
set -euo pipefail

api=http://localhost:8000
mailpit=http://localhost:8025/api/v1
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')

fail() { echo "::error::$1"; exit 1; }
sql() { docker compose exec -T db psql -U postgres -d infrawatch -qtAc "$1"; }
code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
token() {
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
as() { local who=$1; shift; curl -fsS -H "Authorization: Bearer ${!who}" "${json[@]}" "$@"; }
mail() { # <subject text>: prints Mailpit's search result for messages with that subject
  curl -fsS -G "${mailpit}/search" --data-urlencode "query=subject:\"$1\""
}
wait_for_mail() { # <subject text> <seconds>
  for _ in $(seq "$2"); do
    case "$(mail "$1")" in *'"messages_count":1'*) return 0 ;; esac
    sleep 1
  done
  fail "no single email with subject \"$1\" after $2 s: $(mail "$1")"
}
addressed() { # <subject text> <field To|Cc> <address>...: the email lists exactly these
  local found expected=""
  found=$(mail "$1" | sed -E "s/.*\"$2\":(\[[^]]*\]|null).*/\1/" | { grep -o '"Address":"[^"]*"' || true; } \
    | cut -d'"' -f4 | sort | tr '\n' ' ')
  [ $# -gt 2 ] && expected=$(printf '%s\n' "${@:3}" | sort | tr '\n' ' ')
  [ "${found}" = "${expected}" ] || fail "\"$1\" $2 is [${found}], expected [${expected}]"
}

support=$(token support)
developer=$(token developer)
sre=$(token sre)
commander=$(token commander)

teams=$(as developer "${api}/teams")
team_of() { sed -E "s/.*\"id\":\"([^\"]+)\",\"name\":\"$1\".*/\1/" <<<"${teams}"; }
user_of() { sed -E "s/.*\"id\":\"([^\"]+)\",\"display_name\":\"$1\".*/\1/" <<<"${teams}"; }
payments=$(team_of "Payments Platform")
infra=$(team_of "Core Infrastructure")
dev_id=$(user_of "Demo Developer")
sre_id=$(user_of "Demo SRE")
# Earlier runs give Core Infrastructure a rotation; it must start without one.
sql "DELETE FROM oncall_members WHERE team_id = '${infra}'; DELETE FROM oncall_rotations WHERE team_id = '${infra}'"

echo "G4.5: a team edits its own rotation, and only its own"
rotation() { echo "{\"members\":[$1],\"handover_local\":\"2026-01-05T09:00:00\",\"time_zone\":\"${2:-UTC}\",\"shift_days\":7}"; }
put() { code -X PUT -H "Authorization: Bearer ${!1}" "${json[@]}" -d "$3" "${api}/teams/$2/oncall"; }
[ "$(put sre "${payments}" "$(rotation "\"${sre_id}\"")")" = 403 ] || fail "an SRE set the payments rotation"
[ "$(put developer "${payments}" "$(rotation "\"${sre_id}\"")")" = 422 ] || fail "someone outside the team was put on call"
[ "$(put developer "${payments}" "$(rotation "\"${dev_id}\"" Mars/Olympus)")" = 422 ] || fail "an unknown time zone was accepted"
[ "$(put developer "${payments}" "$(rotation "\"${dev_id}\"")")" = 200 ] || fail "the payments lead could not set their rotation"

echo "G4.3: raising sends one email to the group with the on-call in CC"
raise='{"title":"Checkout errors","impact":"Some customers cannot pay","description":"5xx","severity":"P2","service":"checkout"}'
created=$(as support -d "${raise}" "${api}/incidents")
id=$(sed -E 's/^\{"id":"([^"]+)".*/\1/' <<<"${created}")
number=$(sed -E 's/.*"number":([0-9]+).*/\1/' <<<"${created}")
wait_for_mail "#${number} Raised" 30
addressed "#${number} Raised" To payments-team@infrawatch.local
addressed "#${number} Raised" Cc developer@infrawatch.local

echo "G4.4 and G4.7: major changes email, minor ones do not; a team with no on-call is flagged"
move() { as "$1" -o /dev/null -d "{\"status\":\"$2\"}" "${api}/incidents/${id}/status"; }
move developer acknowledged
as commander -o /dev/null -d '{"severity":"P1"}' "${api}/incidents/${id}/severity"
wait_for_mail "#${number} Severity changed" 30
as developer -o /dev/null -d "{\"team_id\":\"${infra}\"}" "${api}/incidents/${id}/teams"
wait_for_mail "#${number} Your team was added" 30
addressed "#${number} Your team was added" To infra-team@infrawatch.local
addressed "#${number} Your team was added" Cc
wait_for_mail "Core Infrastructure has no on-call for #${number}" 30
addressed "Core Infrastructure has no on-call for #${number}" To admin@infrawatch.local

echo "G4.5: once the team has a rotation, the CC follows it"
[ "$(put sre "${infra}" "$(rotation "\"${sre_id}\"")")" = 200 ] || fail "the infra lead could not set their rotation"
for next in investigating mitigating monitoring resolved; do move commander "${next}"; done
wait_for_mail "#${number} Resolved" 30
addressed "#${number} Resolved" To infra-team@infrawatch.local payments-team@infrawatch.local
addressed "#${number} Resolved" Cc developer@infrawatch.local sre@infrawatch.local
total=$(mail "#${number} " | sed -E 's/.*"messages_count":([0-9]+).*/\1/')
# Raised, severity, team added, the admin's no-on-call email and Resolved: none for the four steps.
[ "${total}" = 5 ] || fail "expected 5 emails for #${number} (none for minor steps), found ${total}"

echo "Mail outage: the incident is raised anyway and the email follows once mail is back"
docker compose stop mailpit >/dev/null 2>&1
second=$(as support -d "${raise}" "${api}/incidents" | sed -E 's/.*"number":([0-9]+).*/\1/') \
  || fail "raising failed while mail was down"
pending="SELECT attempts > 0 AND sent_at IS NULL FROM outbox o JOIN incidents i ON i.id = o.incident_id
  WHERE i.number = ${second} AND o.kind = 'incident.raised'"
for _ in $(seq 30); do [ "$(sql "${pending}")" = t ] && break; sleep 1; done
[ "$(sql "${pending}")" = t ] || fail "the failed delivery was not recorded for a retry"
docker compose start mailpit >/dev/null 2>&1
docker compose up --wait mailpit >/dev/null 2>&1
wait_for_mail "#${second} Raised" 120

[ "$(sql "SELECT count(*) FROM audit_log WHERE action = 'oncall.update' AND target_id = '${infra}'")" -ge 1 ] \
  || fail "no audit row for the rotation change"

echo "notifications: one email per major event to the groups with the on-call in CC, the admin told about a missing on-call, and mail outages only delay delivery"

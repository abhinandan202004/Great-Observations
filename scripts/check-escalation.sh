#!/usr/bin/env bash
# G4.6 against the running stack: an incident nobody acknowledges escalates to the next person in
# the rotation after the timer, the escalation is recorded and emailed, and it stops when the
# rotation is used up. Acknowledged incidents and severities without a timer never escalate.
# Raise times are moved back in the database so the check does not wait real minutes.
set -euo pipefail

api=http://localhost:8000
mailpit=http://localhost:8025/api/v1
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')

fail() { echo "::error::$1"; exit 1; }
sql() { docker compose exec -T db psql -U postgres -d infrawatch -qtAc "$1"; }
token() {
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
as() { local who=$1; shift; curl -fsS -H "Authorization: Bearer ${!who}" "${json[@]}" "$@"; }
raise() { # <severity>: prints the new incident's id
  as support -d "{\"title\":\"Escalation check\",\"impact\":\"Checkout slow\",\"description\":\"x\",\"severity\":\"$1\",\"service\":\"checkout\"}" \
    "${api}/incidents" | sed -E 's/^\{"id":"([^"]+)".*/\1/'
}
backdate() { sql "UPDATE incidents SET raised_at = raised_at - interval '$2 minutes' WHERE id = '$1'" >/dev/null; }
escalations() { sql "SELECT count(*) FROM escalations WHERE incident_id = '$1'"; }

support=$(token support)
developer=$(token developer)
admin=$(token admin)

teams=$(as developer "${api}/teams")
payments=$(sed -E 's/.*"id":"([^"]+)","name":"Payments Platform".*/\1/' <<<"${teams}")
dev=$(sed -E 's/.*"id":"([^"]+)","display_name":"Demo Developer".*/\1/' <<<"${teams}")
dev2=$(sed -E 's/.*"id":"([^"]+)","display_name":"Demo Developer Two".*/\1/' <<<"${teams}")
as developer -o /dev/null -X PUT "${api}/teams/${payments}/oncall" -d "{\"members\":[\"${dev}\",\"${dev2}\"],
  \"handover_local\":\"2026-01-05T09:00:00\",\"time_zone\":\"UTC\",\"shift_days\":7}"
# Whoever is on call this week, the other one is next. Teams come sorted by name, so the last
# on_call in the list is Payments Platform's.
on_call=$(as developer "${api}/oncall" | sed -E 's/.*"on_call":\{"id":"([^"]+)".*/\1/')
if [ "${on_call}" = "${dev}" ]; then next=developer2; else next=developer; fi

echo "The SLA policy keeps its escalation timer when an update leaves it out"
as admin -o /dev/null -X PUT "${api}/sla-policies/P2" -d '{"acknowledge_minutes":15,"resolve_minutes":480}'
as admin "${api}/sla-policies" | grep -q '"escalate_minutes":10,"severity":"P2"' \
  || fail "updating P2 without escalate_minutes cleared its escalation timer"

echo "G4.6: an unacknowledged P2 escalates to ${next}@ after 10 minutes"
id=$(raise P2)
number=$(sql "SELECT number FROM incidents WHERE id = '${id}'")
backdate "${id}" 11
for _ in $(seq 45); do [ "$(escalations "${id}")" = 1 ] && break; sleep 1; done
[ "$(escalations "${id}")" = 1 ] || fail "the incident did not escalate"
[ "$(sql "SELECT u.email FROM escalations e JOIN users u ON u.id = e.to_user_id WHERE e.incident_id = '${id}'")" \
  = "${next}@infrawatch.local" ] || fail "it escalated to the wrong person"
search() { curl -fsS -G "${mailpit}/search" --data-urlencode "query=subject:\"#${number} Escalated to you\""; }
for _ in $(seq 30); do case "$(search)" in *'"messages_count":1'*) break ;; esac; sleep 1; done
case "$(search)" in *"\"To\":[{\"Name\":\"\",\"Address\":\"${next}@infrawatch.local\"}],\"Cc\":[{\"Name\":\"\",\"Address\":\"payments-team@infrawatch.local\"}]"*) ;;
  *) fail "no escalation email to ${next}@ with the group in CC: $(search)" ;; esac
as developer "${api}/incidents/${id}" | grep -q '"escalations":\[{"time":"[^"]*","team":"Payments Platform","step":1' \
  || fail "the incident does not show its escalation"

echo "It stops once everyone else in the rotation has been asked"
backdate "${id}" 30
sleep 20 # more than one sweep
[ "$(escalations "${id}")" = 1 ] || fail "it escalated past the end of the rotation"

echo "An acknowledged incident and a P4 never escalate"
acked=$(raise P2)
as developer -o /dev/null -d '{"status":"acknowledged"}' "${api}/incidents/${acked}/status"
low=$(raise P4)
backdate "${acked}" 30
backdate "${low}" 600
sleep 20
[ "$(escalations "${acked}")" = 0 ] || fail "an acknowledged incident escalated"
[ "$(escalations "${low}")" = 0 ] || fail "a P4 escalated"

[ "$(sql "SELECT count(*) FROM audit_log WHERE action = 'incident.escalate' AND target_id = '${id}'")" = 1 ] \
  || fail "the escalation has no audit row"

echo "escalation: unacknowledged incidents pass along the rotation once per timer, recorded and emailed, and stop when acknowledged or the rotation runs out"

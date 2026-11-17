#!/usr/bin/env bash
# G3.2, G3.3, G3.7, G3.8 and G8.5 against the running API: raise, the status lifecycle with its
# scoped rules, caller-only close and reopen, severity changes, the status-only view and audit rows.
set -euo pipefail

api=http://localhost:8000
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')

fail() { echo "::error::$1"; exit 1; }
token() { # <seeded user name>
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
move() { # <token> <status> [reason]: prints the HTTP status of the transition
  local reason=${3:+,\"reason\":\"$3\"}
  code -H "Authorization: Bearer $1" "${json[@]}" -d "{\"status\":\"$2\"${reason}}" \
    "${api}/incidents/${id}/status"
}
expect() { # <expected code> <actual code> <message>
  [ "$2" = "$1" ] || fail "$3 (got $2, expected $1)"
}

support=$(token support)
developer=$(token developer) # lead of Payments Platform, which owns checkout
sre=$(token sre)             # Core Infrastructure: not on this incident
commander=$(token commander)
viewer=$(token viewer)
stakeholder=$(token stakeholder)

raise='{"title":"Checkout errors","impact":"Some customers cannot pay","description":"5xx on POST /checkout","severity":"P2","service":"checkout"}'
expect 403 "$(code -H "Authorization: Bearer ${developer}" "${json[@]}" -d "${raise}" "${api}/incidents")" \
  "a developer raised an incident"
id=$(curl -fsS -H "Authorization: Bearer ${support}" "${json[@]}" -d "${raise}" "${api}/incidents" \
  | sed -E 's/^\{"id":"([^"]+)".*/\1/')

# G8.5: viewers and stakeholders get status and impact, never the description or timeline.
for who in "${viewer}" "${stakeholder}"; do
  body=$(curl -fsS -H "Authorization: Bearer ${who}" "${api}/incidents/${id}")
  case "${body}" in *'"impact"'*) ;; *) fail "the status-only view has no impact: ${body}" ;; esac
  case "${body}" in *'"description"'* | *'"timeline"'*) fail "the status-only view leaks detail" ;; esac
done

# G3.2 and G3.3: scoped updates, one step at a time, regressions need a reason.
expect 403 "$(move "${sre}" acknowledged)" "a member of an uninvolved team changed the status"
expect 200 "$(move "${developer}" acknowledged)" "the owning team could not acknowledge"
expect 409 "$(move "${developer}" mitigating)" "a skipped state was accepted"
expect 200 "$(move "${developer}" investigating)" "acknowledged to investigating failed"
expect 422 "$(move "${developer}" acknowledged)" "a regression without a reason was accepted"
expect 200 "$(move "${developer}" acknowledged 'wrong team picked it up')" "a regression with a reason failed"
for next in investigating mitigating monitoring resolved; do
  expect 200 "$(move "${commander}" "${next}")" "the incident commander could not move to ${next}"
done

# G3.7: only the caller may close; until runbooks exist (M7) even the caller is refused.
expect 403 "$(move "${developer}" closed)" "a developer closed the incident"
expect 403 "$(move "${commander}" closed)" "the incident commander closed the incident"
expect 409 "$(move "${support}" closed)" "the caller closed without an approved runbook"

# G3.8: the caller rejects the resolution with a reason, linked to the earlier resolution.
expect 403 "$(move "${developer}" investigating 'not fixed')" "someone other than the caller reopened"
expect 422 "$(move "${support}" investigating)" "a reopen without a reason was accepted"
expect 200 "$(move "${support}" investigating 'still failing for EU customers')" "the caller could not reopen"
curl -fsS -H "Authorization: Bearer ${support}" "${api}/incidents/${id}" | grep -q '"reopens":[0-9]' \
  || fail "the reopen is not linked to the earlier resolution"

expect 403 "$(code -H "Authorization: Bearer ${developer}" "${json[@]}" -d '{"severity":"P1"}' \
  "${api}/incidents/${id}/severity")" "a developer changed the severity"
expect 200 "$(code -H "Authorization: Bearer ${commander}" "${json[@]}" -d '{"severity":"P1"}' \
  "${api}/incidents/${id}/severity")" "the incident commander could not change the severity"

audit=$(docker compose exec -T db psql -U postgres -d infrawatch -tAc \
  "SELECT string_agg(DISTINCT action, ',') FROM audit_log WHERE target_id = '${id}'")
for action in incident.raise incident.forward incident.regression incident.reopen incident.severity; do
  case ",${audit}," in *",${action},"*) ;; *) fail "no audit row for ${action}: ${audit}" ;; esac
done

echo "incidents: raise, lifecycle, scoped updates, caller-only close and reopen, status-only view and audit rows all behave"

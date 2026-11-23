#!/usr/bin/env bash
# G5.1 to G5.5 and G3.7 against the running stack: the runbook is written at Resolved by an
# engineer on a working team, every field is enforced by the server, the root cause comes from the
# taxonomy, someone other than the author approves or returns it, only then can the caller close,
# a reopen needs a fresh approval, and approved runbooks are versioned and searchable.
set -euo pipefail

api=http://localhost:8000
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')

fail() { echo "::error::$1"; exit 1; }
token() {
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
code() { local who=$1; shift; curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${!who}" "${json[@]}" "$@"; }
as() { local who=$1; shift; curl -fsS -H "Authorization: Bearer ${!who}" "${json[@]}" "$@"; }
expect() { [ "$2" = "$1" ] || fail "$3 (got $2, expected $1)"; }

support=$(token support)
developer=$(token developer)   # lead of Payments Platform
developer2=$(token developer2) # Payments engineer, not a lead
sre=$(token sre)               # lead of Core Infrastructure, not on these incidents
commander=$(token commander)
viewer=$(token viewer)

word="flux$(date +%s)" # a unique word to search for
raise() {
  as support -d '{"title":"Runbook check","impact":"Checkout failing","description":"x","severity":"P3","service":"checkout"}' \
    "${api}/incidents" | sed -E 's/^\{"id":"([^"]+)".*/\1/'
}
move() { code "$1" -d "{\"status\":\"$3\"${4:+,\"reason\":\"$4\"}}" "${api}/incidents/$2/status"; }
resolve() { for s in acknowledged investigating mitigating monitoring resolved; do move commander "$1" "$s" >/dev/null; done; }
runbook() { # <cause text> [category]: a complete runbook body
  echo "{\"timeline\":\"09:00 detected\",\"root_cause_category\":\"${2:-code_or_deploy}\",\"root_cause\":\"$1\",
    \"contributing_factors\":\"No canary\",\"remediation\":\"Rolled back the deploy\",
    \"workaround\":\"Manual retries, since removed\",\"similar_incident_ids\":[],
    \"none_similar\":\"Searched checkout incidents from the last 90 days\"}"
}
submit() { code "$1" -d "$3" "${api}/incidents/$2/runbook"; }
review() { code "$1" -d "{\"decision\":\"$4\",\"comment\":\"${5:-}\"}" "${api}/incidents/$2/runbook/$3/review"; }

id=$(raise)
echo "G5.1: the runbook is written once the incident is Resolved"
expect 409 "$(submit developer "${id}" "$(runbook "Too early")")" "a runbook was accepted before Resolved"
resolve "${id}"
expect 409 "$(move support "${id}" closed)" "the caller closed without a runbook"

echo "G5.2 and G5.3: every field is required, and the category comes from the taxonomy"
expect 422 "$(submit developer "${id}" "$(runbook "")")" "an empty root cause was accepted"
expect 422 "$(submit developer "${id}" "$(runbook "x" | sed 's/"none_similar":"[^"]*"/"none_similar":""/')")" \
  "a runbook with no similar incidents and no statement was accepted"
expect 422 "$(submit developer "${id}" "$(runbook "x" weather)")" "a category outside the taxonomy was accepted"
expect 403 "$(submit sre "${id}" "$(runbook "x")")" "an engineer from an uninvolved team wrote the runbook"
expect 403 "$(submit commander "${id}" "$(runbook "x")")" "the incident commander wrote the runbook"
expect 201 "$(submit developer "${id}" "$(runbook "Deploy ${word} disabled the payment retry")")" \
  "the payments lead could not submit a complete runbook"
expect 409 "$(submit developer2 "${id}" "$(runbook "Second try")")" "a second version was accepted while one awaits review"

echo "G5.4: someone other than the author reviews; a return needs a reason"
expect 403 "$(review developer "${id}" 1 approved)" "the author approved their own runbook"
expect 403 "$(review developer2 "${id}" 1 approved)" "an engineer who is not a lead approved it"
expect 403 "$(review sre "${id}" 1 approved)" "a lead of an uninvolved team approved it"
expect 422 "$(review commander "${id}" 1 returned)" "a runbook was returned without comments"
expect 200 "$(review commander "${id}" 1 returned "Name the deploy and its version")" "the commander could not return it"
expect 409 "$(move support "${id}" closed)" "the caller closed with only a returned runbook"
expect 201 "$(submit developer2 "${id}" "$(runbook "Deploy ${word} v2.3 disabled the payment retry")")" \
  "an engineer on the team could not resubmit"
expect 200 "$(review developer "${id}" 2 approved)" "a lead who did not write version 2 could not approve it"

echo "G3.7: now only the caller may close"
expect 403 "$(move developer "${id}" closed)" "someone other than the caller closed the incident"
expect 200 "$(move support "${id}" closed)" "the caller could not close after approval"

echo "A reopened incident needs a fresh approval before it can close again"
second=$(raise)
resolve "${second}"
expect 201 "$(submit developer "${second}" "$(runbook "Capacity ran out" capacity_or_infrastructure)")" "could not submit"
expect 200 "$(review commander "${second}" 1 approved)" "could not approve"
expect 200 "$(move support "${second}" investigating "Still failing for EU customers")" "the caller could not reopen"
resolve "${second}"
expect 409 "$(move support "${second}" closed)" "an approval from before the reopen let the caller close"

echo "G5.5: approved runbooks are versioned and searchable"
hits=$(as developer "${api}/runbooks/search?q=${word}")
case "${hits}" in *"\"version\":2"*"${word} v2.3"*) ;; *) fail "search did not find the approved version 2: ${hits}" ;; esac
case "$(as developer "${api}/runbooks/search?q=${word}&category=data")" in "[]") ;; *) fail "the category filter let other categories through" ;; esac
as developer "${api}/incidents/${id}/runbook" | grep -q '"version":1,.*"decision":"returned".*"version":2,.*"decision":"approved"' \
  || fail "the incident does not keep both versions with their reviews"
expect 403 "$(code viewer "${api}/runbooks/search?q=${word}")" "a viewer searched runbooks"

echo "runbooks: written at Resolved, every field enforced, reviewed by someone else, closing gated on approval, reopen needs a fresh approval, versions searchable"

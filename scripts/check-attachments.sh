#!/usr/bin/env bash
# G3.1 (attachments), G4.1, G4.2 and G8.5 against the running stack: a metric snapshot stays
# frozen while new samples arrive, log excerpts keep their lines and correlation ids, links must be
# http(s), files go to object storage only within the size limit and type allowlist, downloads are
# served as inert attachments, and viewers and stakeholders cannot see any of it.
set -euo pipefail

api=http://localhost:8000
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

fail() { echo "::error::$1"; exit 1; }
sql() { docker compose exec -T db psql -U postgres -d infrawatch -qtAc "$1"; }
token() {
  curl -fsS "${json[@]}" -d "{\"email\":\"$1@infrawatch.local\",\"password\":\"${password}\"}" \
    "${api}/auth/login" | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}
code() { local who=$1; shift; curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${!who}" "$@"; }
as() { local who=$1; shift; curl -fsS -H "Authorization: Bearer ${!who}" "$@"; }
upload() { # <who> <file> <name>: prints the HTTP status
  code "$1" -H 'Content-Type: application/octet-stream' --data-binary "@$2" \
    "${api}/incidents/${id}/attachments/file?name=$3"
}
expect() { [ "$2" = "$1" ] || fail "$3 (got $2, expected $1)"; }
ago() { date -u -d "-$1" +%Y-%m-%dT%H:%M:%SZ; }

support=$(token support)
developer=$(token developer)
sre=$(token sre)
viewer=$(token viewer)
stakeholder=$(token stakeholder)

id=$(as support "${json[@]}" -d '{"title":"Attachment check","impact":"Checkout errors","description":"x","severity":"P3","service":"checkout"}' \
  "${api}/incidents" | sed -E 's/^\{"id":"([^"]+)".*/\1/')
attachments() { as developer "${api}/incidents/${id}/attachments"; }

echo "G4.1: a metric snapshot is frozen at the moment it is attached"
snapshot="{\"service\":\"checkout\",\"metric\":\"error_rate_percent\",\"since\":\"$(ago '10 min')\",\"until\":\"$(ago '0 min')\"}"
expect 403 "$(code sre "${json[@]}" -d "${snapshot}" "${api}/incidents/${id}/attachments/snapshot")" \
  "a member of an uninvolved team attached evidence"
expect 201 "$(code developer "${json[@]}" -d "${snapshot}" "${api}/incidents/${id}/attachments/snapshot")" \
  "the owning team could not attach a snapshot"
before=$(attachments)
sleep 10 # new samples arrive meanwhile
[ "$(attachments)" = "${before}" ] || fail "the snapshot changed after it was attached"
[ "$(sql "SELECT has_table_privilege('infrawatch_app', 'attachments', 'UPDATE') OR has_table_privilege('infrawatch_app', 'attachments', 'DELETE')")" = f ] \
  || fail "the app role can change or remove attachments"

echo "Log excerpts keep the selected lines with their correlation ids"
ids=$(as developer "${api}/logs?service=checkout&since=$(ago '30 min')&limit=3" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 \
  | sed 's/.*/"&"/' | paste -sd, -)
[ -n "${ids}" ] || fail "no checkout log lines to excerpt"
expect 201 "$(code developer "${json[@]}" -d "{\"ids\":[${ids}]}" "${api}/incidents/${id}/attachments/logs")" \
  "the team could not attach a log excerpt"
attachments | grep -q '"kind":"log_excerpt".*"correlation_id"' || fail "the excerpt lost its correlation ids"

echo "Links must be http(s); notes are free text"
expect 422 "$(code developer "${json[@]}" -d '{"text":"x","url":"javascript:alert(1)"}' "${api}/incidents/${id}/attachments/note")" \
  "a javascript: link was accepted"
expect 201 "$(code developer "${json[@]}" -d '{"text":"Runbook","url":"https://example.com/runbook"}' "${api}/incidents/${id}/attachments/note")" \
  "the team could not attach a link"
expect 201 "$(code support "${json[@]}" -d '{"text":"Customer reports started at 09:40"}' "${api}/incidents/${id}/attachments/note")" \
  "the caller could not attach a note"

echo "G4.2: files reach object storage only within the size limit and the type allowlist"
printf '\x89PNG\r\n\x1a\nnot really an image' > "$work/shot.png"
printf '<!doctype html><script>alert(1)</script>' > "$work/page.html"
head -c 10485761 /dev/zero > "$work/big.png"
expect 403 "$(upload sre "$work/shot.png" shot.png)" "a member of an uninvolved team uploaded a file"
expect 415 "$(upload developer "$work/page.html" page.html)" "an HTML file was accepted"
expect 415 "$(upload developer "$work/page.html" fake.png)" "HTML named .png was accepted"
expect 413 "$(upload developer "$work/big.png" big.png)" "a file over 10 MB was accepted"
expect 201 "$(upload developer "$work/shot.png" shot.png)" "a PNG within the limit was refused"
file=$(attachments | sed -E 's/.*"id":"([^"]+)","kind":"file".*/\1/')

echo "Downloads come back byte for byte, as inert attachments"
as developer -D "$work/headers" -o "$work/back.png" "${api}/attachments/${file}/file"
cmp -s "$work/shot.png" "$work/back.png" || fail "the downloaded file differs from the upload"
for header in "content-type: image/png" "content-disposition: attachment; filename\*=UTF-8''shot.png" \
  "x-content-type-options: nosniff" "content-security-policy: default-src 'none'; frame-ancestors 'none'; sandbox"; do
  grep -qi "^${header}" "$work/headers" || fail "the download lacks the header ${header}"
done

echo "G8.5: viewers and stakeholders see no attachments"
for who in viewer stakeholder; do
  expect 403 "$(code "${who}" "${api}/incidents/${id}/attachments")" "${who} listed attachments"
  expect 403 "$(code "${who}" "${api}/attachments/${file}/file")" "${who} downloaded a file"
done

[ "$(sql "SELECT count(*) FROM audit_log WHERE action = 'attachment.add' AND target_id = '${id}'")" = 5 ] \
  || fail "not every attachment has an audit row"

echo "attachments: snapshots stay frozen, excerpts keep correlation ids, links are http(s), files are checked and stored, downloads are inert, and status-only roles see none of it"

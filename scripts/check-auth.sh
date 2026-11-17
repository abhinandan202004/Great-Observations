#!/usr/bin/env bash
# G8.2 and G8.4 against the running API: sign-in, the refresh cookie, rotation, reuse, logout,
# role checks for a few roles, and the audit rows. Every role is in the unit tests.
set -euo pipefail

api=http://localhost:8000
email=admin@infrawatch.local
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')
csrf=(-H 'X-InfraWatch-Request: 1')
since="since=2026-01-01T00:00:00Z"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
login() { # <cookie jar> [email]: prints the access token
  curl -fsS -c "$1" "${json[@]}" -d "{\"email\":\"${2:-$email}\",\"password\":\"${password}\"}" "${api}/auth/login" \
    | sed -E 's/.*"access_token":"([^"]+)".*/\1/'
}

[ "$(code "${json[@]}" -d "{\"email\":\"${email}\",\"password\":\"wrong\"}" "${api}/auth/login")" = 401 ] \
  || { echo "::error::a wrong password was not refused"; exit 1; }

token=$(login "$work/jar")
grep -q '#HttpOnly_.*infrawatch_refresh' "$work/jar" || { echo "::error::refresh cookie is not HttpOnly"; exit 1; }
[ "$(code -H "Authorization: Bearer ${token}" "${api}/auth/me")" = 200 ] || { echo "::error::/auth/me refused a fresh token"; exit 1; }
[ "$(code "${api}/auth/me")" = 401 ] || { echo "::error::/auth/me answered without a token"; exit 1; }

[ "$(code -b "$work/jar" -X POST "${api}/auth/refresh")" = 403 ] || { echo "::error::refresh ran without the CSRF header"; exit 1; }

cp "$work/jar" "$work/first"
[ "$(code -b "$work/first" -c "$work/jar" "${csrf[@]}" -X POST "${api}/auth/refresh")" = 200 ] \
  || { echo "::error::refresh with a valid cookie failed"; exit 1; }
[ "$(code -b "$work/first" "${csrf[@]}" -X POST "${api}/auth/refresh")" = 401 ] \
  || { echo "::error::a rotated refresh token was accepted again"; exit 1; }
[ "$(code -b "$work/jar" "${csrf[@]}" -X POST "${api}/auth/refresh")" = 401 ] \
  || { echo "::error::reuse did not revoke the rest of the login"; exit 1; }

login "$work/second" > /dev/null
[ "$(code -b "$work/second" "${csrf[@]}" -X POST "${api}/auth/logout")" = 204 ] || { echo "::error::logout failed"; exit 1; }
[ "$(code -b "$work/second" "${csrf[@]}" -X POST "${api}/auth/refresh")" = 401 ] \
  || { echo "::error::a refresh token worked after logout"; exit 1; }

# Role checks on the live API for a few roles (the unit tests cover all eight).
[ "$(code "${api}/services")" = 401 ] || { echo "::error::/services answered without a token"; exit 1; }
viewer=$(login "$work/viewer" viewer@infrawatch.local)
[ "$(code -H "Authorization: Bearer ${viewer}" "${api}/services")" = 200 ] || { echo "::error::viewer was refused telemetry"; exit 1; }
[ "$(code -H "Authorization: Bearer ${viewer}" "${api}/logs?${since}")" = 403 ] || { echo "::error::viewer could read logs"; exit 1; }
stakeholder=$(login "$work/stakeholder" stakeholder@infrawatch.local)
[ "$(code -H "Authorization: Bearer ${stakeholder}" "${api}/services")" = 403 ] || { echo "::error::stakeholder could read telemetry"; exit 1; }
[ "$(code -H "Authorization: Bearer ${token}" "${api}/logs?${since}")" = 200 ] || { echo "::error::admin was refused logs"; exit 1; }

# Every sign-in, the reuse and the logout left an audit row.
audit=$(docker compose exec -T db psql -U postgres -d infrawatch -tAc \
  "SELECT coalesce(string_agg(DISTINCT action, ',' ORDER BY action), '') FROM audit_log")
for action in auth.login auth.refresh auth.refresh_reuse auth.logout; do
  case "${audit}" in *"${action}"*) ;; *) echo "::error::no audit row for ${action}: ${audit}"; exit 1 ;; esac
done

echo "auth: sign-in, cookie, rotation, reuse, logout, role checks and audit rows all behave"

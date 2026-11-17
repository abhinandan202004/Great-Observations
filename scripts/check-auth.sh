#!/usr/bin/env bash
# G8.2 against the running API: sign-in, the refresh cookie, rotation, reuse and logout.
# Expiry and signature checks are unit tests (apps/api/tests/test_auth.py).
set -euo pipefail

api=http://localhost:8000
email=admin@infrawatch.local
password=$(grep '^DEMO_USER_PASSWORD=' .env | cut -d= -f2-)
json=(-H 'Content-Type: application/json')
csrf=(-H 'X-InfraWatch-Request: 1')
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }
login() { # <cookie jar>: prints the access token
  curl -fsS -c "$1" "${json[@]}" -d "{\"email\":\"${email}\",\"password\":\"${password}\"}" "${api}/auth/login" \
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

echo "auth: login, HttpOnly cookie, rotation, reuse revokes the login, and logout all behave"

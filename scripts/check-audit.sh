#!/usr/bin/env bash
# G8.4 at the database layer: the app role cannot change the audit log, and the trigger
# refuses changes even from a superuser. Run after the stack is up and migrated.
set -euo pipefail

sql() { docker compose exec -T db psql -U postgres -d infrawatch -tAc "$1" 2>&1; }

for privilege in INSERT SELECT; do
  [ "$(sql "SELECT has_table_privilege('infrawatch_app', 'audit_log', '${privilege}')")" = t ] \
    || { echo "::error::infrawatch_app may not ${privilege} audit_log"; exit 1; }
done
for privilege in UPDATE DELETE TRUNCATE; do
  [ "$(sql "SELECT has_table_privilege('infrawatch_app', 'audit_log', '${privilege}')")" = f ] \
    || { echo "::error::infrawatch_app may ${privilege} audit_log"; exit 1; }
done

for statement in "UPDATE audit_log SET action = action WHERE false" \
                 "DELETE FROM audit_log WHERE false" \
                 "TRUNCATE audit_log"; do
  out=$(sql "${statement}" || true)
  case "${out}" in *"append-only"*) ;; *) echo "::error::not refused by the trigger: ${statement}: ${out}"; exit 1 ;; esac
done
echo "audit_log: the app role can only insert and read; the trigger refuses UPDATE, DELETE and TRUNCATE"

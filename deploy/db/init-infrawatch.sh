#!/usr/bin/env bash
# Superuser-only setup on first start: roles, database and extensions.
# The schema itself lives in the API's Alembic migrations, run as infrawatch_owner.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-postgres}" --dbname postgres \
  -v owner_password="${DB_OWNER_PASSWORD}" -v app_password="${DB_APP_PASSWORD}" <<'SQL'
CREATE ROLE infrawatch_owner LOGIN PASSWORD :'owner_password';
CREATE ROLE infrawatch_app LOGIN PASSWORD :'app_password';
CREATE DATABASE infrawatch OWNER infrawatch_owner;
REVOKE ALL ON DATABASE infrawatch FROM PUBLIC;
GRANT CONNECT ON DATABASE infrawatch TO infrawatch_app;
\connect infrawatch
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;
SQL

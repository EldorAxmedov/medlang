#!/usr/bin/env bash
set -euo pipefail

# Safe DB setup script
# This script will only CREATE user and database if they do not already exist.
# It will NOT DROP or ALTER existing databases. Use with care and supply
# an admin user with create privileges via PG_ADMIN_USER / PG_ADMIN_PASSWORD.

: "${PG_ADMIN_USER:=postgres}"
: "${PG_ADMIN_PASSWORD:=}"
: "${POSTGRES_DB:=medlang}"
: "${POSTGRES_USER:=medlang_user}"
: "${POSTGRES_PASSWORD:=change-me-secure-password}"
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"

export PGPASSWORD="$PG_ADMIN_PASSWORD"

PSQL=(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$PG_ADMIN_USER" -v ON_ERROR_STOP=1 -q -t -A)

echo "Checking for existing database '$POSTGRES_DB' on $POSTGRES_HOST:$POSTGRES_PORT..."
DB_EXISTS=$(${PSQL[@]} -c "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'" || echo "")

if [[ "$DB_EXISTS" == "1" ]]; then
  echo "Database '${POSTGRES_DB}' already exists — leaving it intact."
else
  echo "Database '${POSTGRES_DB}' not found. Will create role and database if necessary."

  # Create role if not exists
  USER_EXISTS=$(${PSQL[@]} -c "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" || echo "")
  if [[ "$USER_EXISTS" == "1" ]]; then
    echo "Role '${POSTGRES_USER}' already exists."
  else
    echo "Creating role '${POSTGRES_USER}'..."
    ${PSQL[@]} -c "CREATE ROLE \"${POSTGRES_USER}\" WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';"
  fi

  echo "Creating database '${POSTGRES_DB}' owned by '${POSTGRES_USER}'..."
  ${PSQL[@]} -c "CREATE DATABASE \"${POSTGRES_DB}\" OWNER \"${POSTGRES_USER}\";"
  echo "Database created."
fi

echo "Setup complete."

unset PGPASSWORD

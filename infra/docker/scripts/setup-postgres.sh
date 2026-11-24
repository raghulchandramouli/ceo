#!/bin/sh
set -eu

: "${POSTGRES_SEEDS:?ERROR: POSTGRES_SEEDS environment variable is required}"
: "${POSTGRES_USER:?ERROR: POSTGRES_USER environment variable is required}"

echo "Waiting for PostgreSQL at ${POSTGRES_SEEDS}:${DB_PORT:-5432}..."
nc -z -w 10 "${POSTGRES_SEEDS}" "${DB_PORT:-5432}"

setup_database() {
  db="$1"
  schema_dir="$2"
  if temporal-sql-tool \
    --plugin postgres12 \
    --ep "${POSTGRES_SEEDS}" \
    -u "${POSTGRES_USER}" \
    -p "${DB_PORT:-5432}" \
    --db "${db}" \
    create
  then
    temporal-sql-tool \
      --plugin postgres12 \
      --ep "${POSTGRES_SEEDS}" \
      -u "${POSTGRES_USER}" \
      -p "${DB_PORT:-5432}" \
      --db "${db}" \
      setup-schema -v 0.0
  else
    echo "Create ${db} did not succeed; continuing with schema update."
  fi
  temporal-sql-tool \
    --plugin postgres12 \
    --ep "${POSTGRES_SEEDS}" \
    -u "${POSTGRES_USER}" \
    -p "${DB_PORT:-5432}" \
    --db "${db}" \
    update-schema -d "${schema_dir}"
}

setup_database temporal /etc/temporal/schema/postgresql/v12/temporal/versioned
setup_database temporal_visibility /etc/temporal/schema/postgresql/v12/visibility/versioned

echo "PostgreSQL schema setup complete"

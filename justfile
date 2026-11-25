set shell := ["bash", "-euo", "pipefail", "-c"]

compose := "docker compose -f infra/docker/docker-compose.yml"

# Start Postgres, Redis, Temporal, and MinIO.
up:
    {{compose}} up -d

# Stop the local stack.
down:
    {{compose}} down

# Apply database migrations.
migrate:
    uv run --directory packages/core alembic upgrade head

# Run the API, Temporal workers, and web console.
dev:
    uv run honcho -f Procfile.dev start

# Run ACL and citation evals.
eval:
    uv run python evals/runner.py

# Regenerate the web API client from the OpenAPI schema.
# `just codegen --check` fails when the committed client has drifted.
codegen *args:
    uv run python scripts/codegen.py {{args}}

# Check formatting, types, package boundaries, and the web app.
lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright
    uv run lint-imports
    pnpm --dir apps/web typecheck

# Format Python.
fmt:
    uv run ruff check --fix .
    uv run ruff format .

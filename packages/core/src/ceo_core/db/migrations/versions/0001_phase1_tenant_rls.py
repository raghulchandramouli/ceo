"""Create Phase 1 tenant tables and enforce row-level security."""

from alembic import op

from ceo_core.db.models import Base
from ceo_core.db.rls import tenant_rls_statements

revision: str = "0001_phase1_tenant_rls"
down_revision: str | None = None


def upgrade() -> None:
    # CREATE EXTENSION and CREATE ROLE cannot run inside Alembic's transaction.
    with op.get_context().autocommit_block():
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector') THEN
                    CREATE EXTENSION IF NOT EXISTS vector;
                END IF;
            END
            $$
            """
        )
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ceo_app') THEN
                    CREATE ROLE ceo_app LOGIN PASSWORD 'ceo_app' NOSUPERUSER NOBYPASSRLS;
                END IF;
                EXECUTE format('GRANT CONNECT ON DATABASE %I TO ceo_app', current_database());
            END
            $$
            """
        )
    op.execute("GRANT USAGE ON SCHEMA public TO ceo_app")

    Base.metadata.create_all(op.get_bind(), checkfirst=False)
    for table in Base.metadata.sorted_tables:
        tenant_column = "id" if table.name == "tenants" else "tenant_id"
        for statement in tenant_rls_statements(table.name, tenant_column):
            op.execute(statement)

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ceo_app")


def downgrade() -> None:
    Base.metadata.drop_all(op.get_bind(), checkfirst=False)

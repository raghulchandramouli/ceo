"""Store per-tenant data keys and ciphertext OAuth tokens."""

import sqlalchemy as sa
from alembic import op

from ceo_core.db.rls import tenant_rls_statements

revision: str = "0002_tenant_data_keys"
down_revision: str | None = "0001_phase1_tenant_rls"


def upgrade() -> None:
    op.create_table(
        "tenant_data_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("wrapped_dek", sa.LargeBinary(), nullable=False),
        sa.UniqueConstraint("tenant_id"),
    )
    op.create_index("ix_tenant_data_keys_tenant_id", "tenant_data_keys", ["tenant_id"])
    op.add_column(
        "connector_installations",
        sa.Column("access_token_ciphertext", sa.LargeBinary(), nullable=True),
    )
    op.add_column(
        "connector_installations",
        sa.Column("refresh_token_ciphertext", sa.LargeBinary(), nullable=True),
    )
    for statement in tenant_rls_statements("tenant_data_keys", "tenant_id"):
        op.execute(statement)
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tenant_data_keys TO ceo_app")


def downgrade() -> None:
    op.drop_column("connector_installations", "refresh_token_ciphertext")
    op.drop_column("connector_installations", "access_token_ciphertext")
    op.drop_index("ix_tenant_data_keys_tenant_id", table_name="tenant_data_keys")
    op.drop_table("tenant_data_keys")

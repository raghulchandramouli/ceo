"""Connector installations and sync cursors."""

from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ceo_core.db.models import TenantOwned


class ConnectorInstallation(TenantOwned):
    __tablename__ = "connector_installations"
    __table_args__ = (UniqueConstraint("tenant_id", "id"),)

    access_token_ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary, default=None)
    refresh_token_ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary, default=None)


class SyncCursor(TenantOwned):
    __tablename__ = "sync_cursors"
    __table_args__ = (
        ForeignKeyConstraint(
            ("tenant_id", "connector_installation_id"),
            ("connector_installations.tenant_id", "connector_installations.id"),
        ),
    )

    connector_installation_id: Mapped[UUID] = mapped_column()

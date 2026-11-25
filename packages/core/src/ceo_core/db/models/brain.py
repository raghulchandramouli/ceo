"""Documents, chunks, and document ACLs."""

from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ceo_core.db.models import TenantOwned


class Document(TenantOwned):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(
            ("tenant_id", "connector_installation_id"),
            ("connector_installations.tenant_id", "connector_installations.id"),
        ),
    )

    connector_installation_id: Mapped[UUID] = mapped_column()


class DocumentChunk(TenantOwned):
    __tablename__ = "document_chunks"
    __table_args__ = (
        ForeignKeyConstraint(("tenant_id", "document_id"), ("documents.tenant_id", "documents.id")),
    )

    document_id: Mapped[UUID] = mapped_column()


class DocumentAcl(TenantOwned):
    __tablename__ = "document_acls"
    __table_args__ = (
        ForeignKeyConstraint(("tenant_id", "document_id"), ("documents.tenant_id", "documents.id")),
    )

    document_id: Mapped[UUID] = mapped_column()

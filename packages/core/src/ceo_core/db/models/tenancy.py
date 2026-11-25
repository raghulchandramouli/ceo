"""Tenants, users, user identities, and workspace policies."""

from uuid import UUID, uuid4

from sqlalchemy import ForeignKeyConstraint, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ceo_core.db.models import Base, TenantOwned


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class User(TenantOwned):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "id"),)


class UserIdentity(TenantOwned):
    __tablename__ = "user_identities"
    __table_args__ = (
        ForeignKeyConstraint(("tenant_id", "user_id"), ("users.tenant_id", "users.id")),
    )

    user_id: Mapped[UUID] = mapped_column()


class WorkspacePolicy(TenantOwned):
    __tablename__ = "workspace_policies"


class TenantDataKey(TenantOwned):
    __tablename__ = "tenant_data_keys"
    __table_args__ = (UniqueConstraint("tenant_id"),)

    wrapped_dek: Mapped[bytes] = mapped_column(LargeBinary)

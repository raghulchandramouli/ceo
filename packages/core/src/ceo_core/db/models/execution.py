"""Agent runs and run steps."""

from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ceo_core.db.models import TenantOwned


class AgentRun(TenantOwned):
    __tablename__ = "agent_runs"
    __table_args__ = (UniqueConstraint("tenant_id", "id"),)


class RunStep(TenantOwned):
    __tablename__ = "run_steps"
    __table_args__ = (
        ForeignKeyConstraint(("tenant_id", "run_id"), ("agent_runs.tenant_id", "agent_runs.id")),
    )

    run_id: Mapped[UUID] = mapped_column()

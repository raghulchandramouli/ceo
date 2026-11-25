"""Async sessions scoped to one tenant per transaction."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import cache
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

DEFAULT_APP_DATABASE_URL = "postgresql+asyncpg://ceo_app:ceo_app@localhost:5432/ceo"


@cache
def _session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, poolclass=NullPool)
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def tenant_session(tenant_id: UUID) -> AsyncGenerator[AsyncSession]:
    database_url = os.environ.get("CEO_APP_DATABASE_URL", DEFAULT_APP_DATABASE_URL)
    async with _session_factory(database_url).begin() as session:
        role = await session.execute(
            text(
                "SELECT rolsuper OR rolbypassrls FROM pg_catalog.pg_roles "
                "WHERE rolname = current_user"
            )
        )
        if role.scalar_one() is not False:
            raise RuntimeError("CEO_APP_DATABASE_URL must use a role subject to row-level security")

        await session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        yield session

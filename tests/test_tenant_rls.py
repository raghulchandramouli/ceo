import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import delete, insert, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from ceo_core.db.models import Base, brain, connectors, execution
from ceo_core.db.models.tenancy import Tenant, User
from ceo_core.db.session import tenant_session


def test_tenant_owned_tables_have_tenant_id() -> None:
    _ = (brain, connectors, execution)
    tables = Base.metadata.tables
    assert set(tables) == {
        "tenants",
        "users",
        "user_identities",
        "workspace_policies",
        "tenant_data_keys",
        "connector_installations",
        "sync_cursors",
        "documents",
        "document_chunks",
        "document_acls",
        "agent_runs",
        "run_steps",
    }
    assert "tenant_id" not in tables["tenants"].columns
    for table in tables.values():
        if table.name != "tenants":
            assert "tenant_id" in table.columns, table.name


def test_application_queries_go_through_tenant_session() -> None:
    repo = Path(__file__).resolve().parents[1]
    allowed = {
        repo / "packages/core/src/ceo_core/db/session.py",
        repo / "packages/core/src/ceo_core/db/migrations/env.py",
    }
    needles = ("create_async_engine", "async_sessionmaker", "async_engine_from_config")
    offenders: list[str] = []
    for root in (repo / "apps", repo / "packages"):
        for path in root.rglob("*.py"):
            if path in allowed or "migrations/versions" in path.as_posix():
                continue
            source = path.read_text(encoding="utf-8")
            if any(needle in source for needle in needles):
                offenders.append(str(path.relative_to(repo)))
    assert offenders == []


def test_tenant_rls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[1] / "packages/core")
    config = Config("alembic.ini")
    database_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    assert database_url is not None
    command.upgrade(config, "head")
    asyncio.run(_assert_user_isolation(database_url))


async def _assert_user_isolation(database_url: str) -> None:
    tenant_a, tenant_b, user_a, user_b = (uuid4() for _ in range(4))
    tenant_ids = (tenant_a, tenant_b)
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(insert(Tenant), [{"id": tenant_a}, {"id": tenant_b}])
            await conn.execute(
                insert(User),
                [{"id": user_a, "tenant_id": tenant_a}, {"id": user_b, "tenant_id": tenant_b}],
            )

        app_url = os.environ.get(
            "CEO_APP_DATABASE_URL",
            "postgresql+asyncpg://ceo_app:ceo_app@localhost:5432/ceo",
        )
        app_engine = create_async_engine(app_url)
        try:
            async with app_engine.connect() as conn:
                unscoped = (await conn.scalars(select(User.id))).all()
            assert unscoped == []
            async with tenant_session(tenant_a) as session:
                setting = await session.scalar(
                    text("SELECT current_setting('app.tenant_id', true)")
                )
                assert setting == str(tenant_a)
                assert (await session.scalars(select(User.id))).all() == [user_a]
                with pytest.raises(DBAPIError, match="violates row-level security policy"):
                    await session.execute(insert(User).values(tenant_id=tenant_b))
        finally:
            await app_engine.dispose()
            async with engine.begin() as conn:
                await conn.execute(delete(User).where(User.tenant_id.in_(tenant_ids)))
                await conn.execute(delete(Tenant).where(Tenant.id.in_(tenant_ids)))
    finally:
        await engine.dispose()

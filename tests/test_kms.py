import asyncio
import logging
import os
from base64 import b64encode
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import create_async_engine

from ceo_core.db.models.tenancy import Tenant, TenantDataKey
from ceo_core.db.session import tenant_session
from ceo_core.security.kms import TokenDecryptionError, decrypt_token, encrypt_token

MASTER_KEY = b64encode(b"\x11" * 32).decode()
ACCESS_TOKEN = "super-secret-access-token"
REFRESH_TOKEN = "super-secret-refresh-token"


def test_kms_envelope_is_per_tenant_and_logs_no_plaintext(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("CEO_KMS_MASTER_KEY", MASTER_KEY)
    monkeypatch.chdir(Path(__file__).resolve().parents[1] / "packages/core")
    config = Config("alembic.ini")
    database_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    assert database_url is not None
    command.upgrade(config, "head")
    caplog.set_level(logging.INFO, logger="ceo_core.security.kms")
    asyncio.run(_assert_envelope(database_url, caplog))


async def _assert_envelope(database_url: str, caplog: pytest.LogCaptureFixture) -> None:
    tenant_a, tenant_b = uuid4(), uuid4()
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(insert(Tenant), [{"id": tenant_a}, {"id": tenant_b}])

        async with tenant_session(tenant_a) as session:
            blob_a = await encrypt_token(session, tenant_a, ACCESS_TOKEN)
            opened = await decrypt_token(session, tenant_a, blob_a)
            wrapped_a = await session.scalar(select(TenantDataKey.wrapped_dek))
        assert opened == ACCESS_TOKEN
        assert ACCESS_TOKEN.encode() not in blob_a
        assert wrapped_a is not None

        async with tenant_session(tenant_b) as session:
            blob_b = await encrypt_token(session, tenant_b, REFRESH_TOKEN)
            wrapped_b = await session.scalar(select(TenantDataKey.wrapped_dek))
            with pytest.raises(TokenDecryptionError):
                await decrypt_token(session, tenant_b, blob_a)
        assert wrapped_b is not None
        assert wrapped_a != wrapped_b
        assert REFRESH_TOKEN.encode() not in blob_b

        logged = caplog.text
        assert ACCESS_TOKEN not in logged
        assert REFRESH_TOKEN not in logged
    finally:
        await engine.dispose()

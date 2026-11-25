"""Envelope encryption for OAuth tokens.

The master key wraps a random data key. Each tenant has its own data key.
Callers pass the token in and receive ciphertext back. This module never logs
the token.
"""

from __future__ import annotations

import logging
import os
from base64 import b64decode
from uuid import UUID

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ceo_core.db.models.connectors import ConnectorInstallation
from ceo_core.db.models.tenancy import TenantDataKey

log = logging.getLogger("ceo_core.security.kms")


class TokenDecryptionError(Exception):
    """The ciphertext cannot be opened with this tenant's data key."""


def master_key() -> bytes:
    raw = os.environ.get("CEO_KMS_MASTER_KEY")
    if raw is None or raw == "":
        raise RuntimeError("CEO_KMS_MASTER_KEY is required")
    try:
        key = b64decode(raw, validate=True)
    except ValueError as exc:
        raise RuntimeError("CEO_KMS_MASTER_KEY must be base64") from exc
    if len(key) != 32:
        raise RuntimeError("CEO_KMS_MASTER_KEY must decode to 32 bytes")
    return key


def seal(key: bytes, plaintext: bytes) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, None)


def open_sealed(key: bytes, blob: bytes) -> bytes:
    try:
        return AESGCM(key).decrypt(blob[:12], blob[12:], None)
    except InvalidTag as exc:
        raise TokenDecryptionError("token ciphertext failed authentication") from exc


async def load_or_create_dek(session: AsyncSession, tenant_id: UUID) -> bytes:
    existing = await session.scalar(
        select(TenantDataKey).where(TenantDataKey.tenant_id == tenant_id)
    )
    kek = master_key()
    if existing is not None:
        return open_sealed(kek, existing.wrapped_dek)
    dek = os.urandom(32)
    session.add(TenantDataKey(tenant_id=tenant_id, wrapped_dek=seal(kek, dek)))
    await session.flush()
    log.info("created data key for tenant %s", tenant_id)
    return dek


async def encrypt_token(session: AsyncSession, tenant_id: UUID, token: str) -> bytes:
    dek = await load_or_create_dek(session, tenant_id)
    blob = seal(dek, token.encode())
    log.info("encrypted oauth token for tenant %s (%d bytes)", tenant_id, len(blob))
    return blob


async def decrypt_token(session: AsyncSession, tenant_id: UUID, blob: bytes) -> str:
    dek = await load_or_create_dek(session, tenant_id)
    token = open_sealed(dek, blob).decode()
    log.info("decrypted oauth token for tenant %s (%d bytes)", tenant_id, len(blob))
    return token


async def store_installation_tokens(
    session: AsyncSession,
    installation: ConnectorInstallation,
    access_token: str,
    refresh_token: str | None = None,
) -> None:
    installation.access_token_ciphertext = await encrypt_token(
        session, installation.tenant_id, access_token
    )
    if refresh_token is not None:
        installation.refresh_token_ciphertext = await encrypt_token(
            session, installation.tenant_id, refresh_token
        )

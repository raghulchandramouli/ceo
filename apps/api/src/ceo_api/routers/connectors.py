"""Connector install, OAuth callback, and resync."""

from fastapi import APIRouter

router = APIRouter(prefix="/connectors", tags=["connectors"])

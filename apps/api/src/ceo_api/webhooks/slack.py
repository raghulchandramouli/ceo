"""Slack Events API, interactivity, and slash commands.

Verify the request signature, acknowledge immediately, debounce through Redis,
and dispatch a Temporal workflow. Do not call a model or run a sync loop here.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/webhooks/slack", tags=["webhooks"])

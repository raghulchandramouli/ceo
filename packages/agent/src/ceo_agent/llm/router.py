"""Route fast extraction and deeper reasoning through the ZDR client."""

import os
from uuid import UUID

from langchain_core.language_models.chat_models import BaseChatModel

from ceo_agent.llm.client import chat_model


def fast_chat_model(tenant_id: UUID) -> BaseChatModel:
    return chat_model(
        provider="openai",
        model=os.environ.get("CEO_FAST_MODEL", "gpt-4.1-mini"),
        tenant_id=tenant_id,
    )


def reasoning_chat_model(tenant_id: UUID) -> BaseChatModel:
    return chat_model(
        provider="anthropic",
        model=os.environ.get("CEO_REASONING_MODEL", "claude-sonnet-4-5"),
        tenant_id=tenant_id,
    )

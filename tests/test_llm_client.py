import ast
import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from ceo_agent.callbacks import MeteringCallback
from ceo_agent.llm.client import chat_model
from ceo_core.metering.tracker import clear_llm_usage_events, llm_usage_events

PROMPT = "PLAINTEXT_PROMPT_DO_NOT_LOG"
FORBIDDEN_CALLS = ("ChatOpenAI", "ChatAnthropic", "OpenAI", "Anthropic")


def test_only_the_llm_client_constructs_chat_models() -> None:
    repo = Path(__file__).resolve().parents[1]
    allowed = repo / "packages/agent/src/ceo_agent/llm/client.py"
    offenders: list[str] = []
    for root in (repo / "apps", repo / "packages"):
        for path in root.rglob("*.py"):
            if path == allowed:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_CALLS:
                        offenders.append(f"{path.relative_to(repo)}:{node.lineno}")
    assert offenders == []


def _callbacks(model: BaseChatModel) -> list[BaseCallbackHandler]:
    callbacks = model.callbacks
    if callbacks is None:
        return []
    if isinstance(callbacks, list):
        return callbacks
    return list(callbacks.handlers)


def test_chat_model_is_zdr_metered_and_untraced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    clear_llm_usage_events()
    tenant_id = uuid4()

    echo = chat_model(provider="echo", model="echo", tenant_id=tenant_id)
    openai_model = chat_model(provider="openai", model="gpt-4.1-mini", tenant_id=tenant_id)
    anthropic_model = chat_model(
        provider="anthropic",
        model="claude-sonnet-4-5",
        tenant_id=tenant_id,
    )

    assert os.environ["LANGCHAIN_TRACING_V2"] == "false"
    assert os.environ["LANGSMITH_TRACING"] == "false"
    assert isinstance(echo, BaseChatModel)
    assert isinstance(openai_model, ChatOpenAI)
    assert openai_model.store is False
    assert isinstance(anthropic_model, ChatAnthropic)
    for model in (echo, openai_model, anthropic_model):
        assert any(isinstance(callback, MeteringCallback) for callback in _callbacks(model))

    asyncio.run(echo.ainvoke(PROMPT))
    events = llm_usage_events()
    assert len(events) == 1
    assert events[0].tenant_id == tenant_id
    assert events[0].model == "echo"
    assert PROMPT not in repr(events[0])

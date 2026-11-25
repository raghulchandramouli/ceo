"""ZDR LangChain chat models. Every model call is built here."""

from __future__ import annotations

import os
from typing import Literal
from uuid import UUID

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI

from ceo_agent.callbacks import MeteringCallback

Provider = Literal["openai", "anthropic", "echo"]


class EchoChatModel(BaseChatModel):
    """Local model used to prove callbacks run without a provider network call."""

    @property
    def _llm_type(self) -> str:
        return "ceo-echo"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: object = None,
        **kwargs: object,
    ) -> ChatResult:
        del messages, stop, run_manager, kwargs
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="ok"))])


def disable_langsmith_tracing() -> None:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGSMITH_TRACING"] = "false"


def chat_model(*, provider: Provider, model: str, tenant_id: UUID) -> BaseChatModel:
    disable_langsmith_tracing()
    callback = MeteringCallback(tenant_id, model)
    if provider == "openai":
        base_url = os.environ.get("CEO_OPENAI_BASE_URL")
        if base_url:
            return ChatOpenAI(
                model=model,
                base_url=base_url,
                store=False,
                callbacks=[callback],
            )
        return ChatOpenAI(model=model, store=False, callbacks=[callback])
    if provider == "anthropic":
        anthropic = ChatAnthropic(
            model_name=model,
            callbacks=[callback],
            timeout=None,
            stop=None,
        )
        api_url = os.environ.get("CEO_ANTHROPIC_API_URL")
        if api_url:
            anthropic.anthropic_api_url = api_url
        return anthropic
    if provider == "echo":
        return EchoChatModel(callbacks=[callback])
    raise ValueError(f"unsupported model provider: {provider}")

"""LangChain callback that records model usage and ignores prompt text."""

from typing import cast
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from ceo_core.metering.tracker import record_llm_usage


class MeteringCallback(AsyncCallbackHandler):
    def __init__(self, tenant_id: UUID, model: str) -> None:
        super().__init__()
        self.tenant_id = tenant_id
        self.model = model

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        **kwargs: object,
    ) -> None:
        del run_id, kwargs
        raw_usage = response.llm_output.get("token_usage") if response.llm_output else None
        prompt_tokens = 0
        completion_tokens = 0
        if isinstance(raw_usage, dict):
            usage = cast(dict[str, object], raw_usage)
            prompt_tokens = _as_int(usage.get("prompt_tokens", usage.get("input_tokens", 0)))
            completion_tokens = _as_int(
                usage.get("completion_tokens", usage.get("output_tokens", 0))
            )
        record_llm_usage(
            tenant_id=self.tenant_id,
            model=self.model,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
        )


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value

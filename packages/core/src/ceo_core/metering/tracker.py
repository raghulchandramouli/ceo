"""Record metered model calls. Prompt text is never stored here."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LlmUsage:
    tenant_id: UUID
    model: str
    input_tokens: int
    output_tokens: int


_events: list[LlmUsage] = []


def record_llm_usage(
    *,
    tenant_id: UUID,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    _events.append(
        LlmUsage(
            tenant_id=tenant_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    )


def llm_usage_events() -> tuple[LlmUsage, ...]:
    return tuple(_events)


def clear_llm_usage_events() -> None:
    _events.clear()

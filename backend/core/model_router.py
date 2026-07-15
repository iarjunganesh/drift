"""
Model routing for DRIFT.

Every OpenAI call in this codebase must go through get_model(tier) —
never hardcode a model name inline. This keeps cost predictable and
makes the dev/live/final cost strategy a one-line change.

Tiers:
  dev   — gpt-5.6-luna  — cheap iteration. Scout classification,
                           Synthesizer dedup/clustering, prompt tuning.
  live  — gpt-5.6-terra — the on-camera / interactive chat-over-knowledge
                           endpoint. Needs to be reliably sharp live.
  final — gpt-5.6-sol   — captured Insight outputs for the small set of
                           real examples used in the demo. Reserve this
                           tier deliberately — don't burn it on iteration.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from openai import AsyncOpenAI, OpenAI

from backend.core.resilience import ModelCallResilience


class Tier(StrEnum):
    DEV = "dev"
    LIVE = "live"
    FINAL = "final"


MODEL_MAP = {
    Tier.DEV: "gpt-5.6-luna",
    Tier.LIVE: "gpt-5.6-terra",
    Tier.FINAL: "gpt-5.6-sol",
}

_PRICE_PER_MILLION_TOKENS = {
    "gpt-5.6-luna": (1.0, 6.0),
    "gpt-5.6-terra": (2.5, 15.0),
    "gpt-5.6-sol": (5.0, 30.0),
}

EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass(frozen=True)
class TextResponse:
    """A provider response with the number of potentially billable attempts."""

    response: Any
    attempts: int


def get_model(tier: Tier | str) -> str:
    """Resolve a cost tier to a concrete model name.

    Usage:
        model = get_model(Tier.DEV)
        response = client.chat.completions.create(model=model, ...)
    """
    if isinstance(tier, str):
        tier = Tier(tier)
    return MODEL_MAP[tier]


def estimate_response_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate token cost using the router's explicit model-price schedule."""
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts cannot be negative.")
    input_price, output_price = _PRICE_PER_MILLION_TOKENS[model]
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def create_async_client(api_key: str, timeout_seconds: float) -> AsyncOpenAI:
    """Create the sole OpenAI client used by live DRIFT agent calls."""
    return AsyncOpenAI(api_key=api_key, max_retries=0, timeout=timeout_seconds)


def create_client(api_key: str, timeout_seconds: float) -> OpenAI:
    """Create the synchronous client used by the bounded Day 2 batch stages."""
    return OpenAI(api_key=api_key, max_retries=0, timeout=timeout_seconds)


def create_embedding_response(client: OpenAI, inputs: list[str]) -> Any:
    """Create one routed batch embedding request for the configured input texts."""
    return client.embeddings.create(model=EMBEDDING_MODEL, input=inputs)


def create_structured_response(
    client: Any,
    *,
    tier: Tier,
    instructions: str,
    input_text: str,
    schema: dict[str, Any],
    max_output_tokens: int,
) -> Any:
    """Create a synchronous structured Responses API request through the router."""
    return client.responses.create(
        model=get_model(tier),
        instructions=instructions,
        input=input_text,
        max_output_tokens=max_output_tokens,
        reasoning={"effort": "low"},
        text={"format": schema},
    )


async def create_text_response(
    client: AsyncOpenAI,
    *,
    tier: Tier,
    instructions: str,
    input_text: str,
    max_output_tokens: int,
    resilience: ModelCallResilience | None = None,
) -> TextResponse:
    """Generate text through the Responses API with a router-resolved model."""
    async def operation() -> Any:
        return await client.responses.create(
            model=get_model(tier),
            instructions=instructions,
            input=input_text,
            max_output_tokens=max_output_tokens,
            reasoning={"effort": "low"},
        )

    if resilience is None:
        return TextResponse(response=await operation(), attempts=1)
    result = await resilience.execute(operation)
    return TextResponse(response=result.value, attempts=result.attempts)


async def create_async_embedding_response(
    client: AsyncOpenAI,
    inputs: list[str],
) -> Any:
    """Create one routed async embedding request for live retrieval."""
    return await client.embeddings.create(model=EMBEDDING_MODEL, input=inputs)

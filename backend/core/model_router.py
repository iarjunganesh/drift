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

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from openai import AsyncOpenAI, OpenAI

from backend.core.budget import SpendGuard
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, ModelCallResilience, RetryPolicy


class Tier(StrEnum):
    DEV = "dev"
    LIVE = "live"
    FINAL = "final"


MODEL_MAP = {
    Tier.DEV: "gpt-5.6-luna",
    Tier.LIVE: "gpt-5.6-terra",
    Tier.FINAL: "gpt-5.6-sol",
}

EMBEDDING_MODEL = "text-embedding-3-small"

_PRICE_PER_MILLION_TOKENS = {
    "gpt-5.6-luna": (1.0, 6.0),
    "gpt-5.6-terra": (2.5, 15.0),
    "gpt-5.6-sol": (5.0, 30.0),
    EMBEDDING_MODEL: (0.02, 0.0),
}


@dataclass(frozen=True)
class TextResponse:
    """A provider response with the number of potentially billable attempts."""

    response: Any
    attempts: int


@dataclass(frozen=True)
class SyncCallResult:
    """A synchronous provider response with audit-safe cost metadata."""

    response: Any
    attempts: int
    settled_usd: float


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


def create_sync_resilience() -> ModelCallResilience:
    """Build the shared retry/circuit policy for bounded batch model calls."""
    return ModelCallResilience(
        retry_policy=RetryPolicy(
            timeout_seconds=settings.model_timeout_seconds,
            max_attempts=settings.model_max_attempts,
            base_delay_seconds=settings.model_retry_base_seconds,
            max_delay_seconds=settings.model_retry_max_seconds,
        ),
        circuit_breaker=CircuitBreaker(
            failure_threshold=settings.model_circuit_failure_threshold,
            reset_seconds=settings.model_circuit_reset_seconds,
        ),
    )


def _response_cost_usd(response: Any, model: str, fallback_usd: float) -> float:
    """Estimate a routed call from reported usage or settle conservatively."""
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None)
    if not isinstance(input_tokens, int):
        input_tokens = getattr(usage, "prompt_tokens", None)
    output_tokens = getattr(usage, "output_tokens", 0)
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return fallback_usd
    return min(fallback_usd, estimate_response_cost_usd(model, input_tokens, output_tokens))


def _default_spend_guard() -> SpendGuard:
    return SpendGuard(
        settings.spend_ledger_path,
        settings.max_spend_usd,
        settings.spend_alert_usd,
    )


def execute_bounded_sync_call(
    operation: Callable[[], Any],
    *,
    operation_name: str,
    spend_guard: SpendGuard | None = None,
    max_call_usd: float | None = None,
    resilience: ModelCallResilience | None = None,
    model: str | None = None,
) -> SyncCallResult:
    """Reserve a retry envelope and execute a synchronous provider request.

    Calls with reported token usage settle at the router's known model price.
    Unknown usage settles at the configured call cap rather than understating
    spend.
    """
    active_guard = spend_guard or _default_spend_guard()
    active_resilience = resilience or create_sync_resilience()
    cap = max_call_usd if max_call_usd is not None else settings.max_call_usd
    max_attempts = active_resilience.retry_policy.max_attempts
    reserved_usd = cap * max_attempts
    active_guard.reserve(reserved_usd, operation_name)
    try:
        result = active_resilience.execute_sync(operation)
    except BaseException:
        active_guard.settle(reserved_usd, reserved_usd, operation_name)
        raise

    if model is None:
        settled_usd = reserved_usd
    else:
        settled_usd = cap * (result.attempts - 1) + _response_cost_usd(
            result.value, model, cap
        )
    active_guard.settle(reserved_usd, settled_usd, operation_name)
    return SyncCallResult(
        response=result.value,
        attempts=result.attempts,
        settled_usd=settled_usd,
    )


def create_embedding_response(
    client: OpenAI,
    inputs: list[str],
    *,
    spend_guard: SpendGuard | None = None,
    max_call_usd: float | None = None,
    resilience: ModelCallResilience | None = None,
    operation_name: str = "synthesizer.embed",
) -> Any:
    """Create one routed batch embedding request for the configured input texts."""
    return execute_bounded_sync_call(
        lambda: client.embeddings.create(model=EMBEDDING_MODEL, input=inputs),
        operation_name=operation_name,
        spend_guard=spend_guard,
        max_call_usd=max_call_usd,
        resilience=resilience,
        model=EMBEDDING_MODEL,
    ).response


def create_structured_response(
    client: Any,
    *,
    tier: Tier,
    instructions: str,
    input_text: str,
    schema: dict[str, Any],
    max_output_tokens: int,
    spend_guard: SpendGuard | None = None,
    max_call_usd: float | None = None,
    resilience: ModelCallResilience | None = None,
    operation_name: str = "insight.generate",
) -> Any:
    """Create a synchronous structured Responses API request through the router."""
    return create_structured_response_with_audit(
        client,
        tier=tier,
        instructions=instructions,
        input_text=input_text,
        schema=schema,
        max_output_tokens=max_output_tokens,
        spend_guard=spend_guard,
        max_call_usd=max_call_usd,
        resilience=resilience,
        operation_name=operation_name,
    ).response


def create_structured_response_with_audit(
    client: Any,
    *,
    tier: Tier,
    instructions: str,
    input_text: str,
    schema: dict[str, Any],
    max_output_tokens: int,
    spend_guard: SpendGuard | None = None,
    max_call_usd: float | None = None,
    resilience: ModelCallResilience | None = None,
    operation_name: str = "insight.generate",
) -> SyncCallResult:
    """Create a bounded structured response and preserve its call audit."""
    model = get_model(tier)
    return execute_bounded_sync_call(
        lambda: client.responses.create(
            model=model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=max_output_tokens,
            reasoning={"effort": "low"},
            text={"format": schema},
        ),
        operation_name=operation_name,
        spend_guard=spend_guard,
        max_call_usd=max_call_usd,
        resilience=resilience,
        model=model,
    )


async def create_text_response(
    client: AsyncOpenAI,
    *,
    tier: Tier,
    instructions: str,
    input_text: str,
    max_output_tokens: int,
    resilience: ModelCallResilience | None = None,
    text_format: dict[str, Any] | None = None,
) -> TextResponse:
    """Generate text through the Responses API with a router-resolved model.

    Pass ``text_format`` to constrain the reply to a strict JSON schema; the
    provider then returns the structured payload as the response ``output_text``.
    """
    async def operation() -> Any:
        request: dict[str, Any] = dict(
            model=get_model(tier),
            instructions=instructions,
            input=input_text,
            max_output_tokens=max_output_tokens,
            reasoning={"effort": "low"},
        )
        if text_format is not None:
            request["text"] = {"format": text_format}
        return await client.responses.create(**request)

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

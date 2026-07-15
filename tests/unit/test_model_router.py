import pytest

from backend.core.budget import SpendGuard
from backend.core.model_router import (
    Tier,
    create_async_client,
    create_client,
    create_text_response,
    estimate_response_cost_usd,
    execute_bounded_sync_call,
    get_model,
)
from backend.core.resilience import CircuitBreaker, ModelCallResilience, RetryPolicy


class FakeResponses:
    async def create(self, **kwargs):
        return kwargs


class FakeClient:
    responses = FakeResponses()


def test_model_router_resolves_every_tier_and_costs_usage() -> None:
    assert get_model(Tier.DEV) == "gpt-5.6-luna"
    assert get_model("live") == "gpt-5.6-terra"
    assert get_model(Tier.FINAL) == "gpt-5.6-sol"
    assert estimate_response_cost_usd("gpt-5.6-sol", 1_000_000, 1_000_000) == 35

    with pytest.raises(ValueError, match="Token counts"):
        estimate_response_cost_usd("gpt-5.6-terra", -1, 0)


def test_model_router_creates_sync_client_without_environment_credentials() -> None:
    client = create_client("test-key", timeout_seconds=5)
    try:
        assert client.api_key == "test-key"
    finally:
        client.close()


@pytest.mark.asyncio
async def test_model_router_creates_client_and_response_request() -> None:
    client = create_async_client("test-key", timeout_seconds=5)
    try:
        assert client.api_key == "test-key"
    finally:
        await client.close()

    result = await create_text_response(
        FakeClient(),
        tier=Tier.DEV,
        instructions="Instructions",
        input_text="Evidence",
        max_output_tokens=123,
    )
    assert result.attempts == 1
    assert result.response == {
        "model": "gpt-5.6-luna",
        "instructions": "Instructions",
        "input": "Evidence",
        "max_output_tokens": 123,
        "reasoning": {"effort": "low"},
    }


def test_sync_model_call_reserves_retries_and_settles_reported_usage(tmp_path) -> None:
    guard = SpendGuard(tmp_path / "ledger.json", limit_usd=1, alert_usd=0.5)
    resilience = ModelCallResilience(
        RetryPolicy(timeout_seconds=1, max_attempts=2, base_delay_seconds=0, max_delay_seconds=0),
        CircuitBreaker(failure_threshold=2, reset_seconds=1),
    )
    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise TimeoutError("retry")
        return type(
            "Response",
            (),
            {"usage": type("Usage", (), {"input_tokens": 1_000, "output_tokens": 100})()},
        )()

    result = execute_bounded_sync_call(
        operation,
        operation_name="test.sync",
        spend_guard=guard,
        max_call_usd=0.2,
        resilience=resilience,
        model="gpt-5.6-luna",
    )

    assert result.attempts == 2
    assert result.settled_usd == pytest.approx(0.2016)
    assert guard._read().reserved_usd == 0


def test_sync_model_call_settles_reserved_envelope_on_failure(tmp_path) -> None:
    guard = SpendGuard(tmp_path / "ledger.json", limit_usd=1, alert_usd=0.5)
    resilience = ModelCallResilience(
        RetryPolicy(timeout_seconds=1, max_attempts=1, base_delay_seconds=0, max_delay_seconds=0),
        CircuitBreaker(failure_threshold=1, reset_seconds=1),
    )

    with pytest.raises(RuntimeError, match="bad request"):
        execute_bounded_sync_call(
            lambda: (_ for _ in ()).throw(RuntimeError("bad request")),
            operation_name="test.sync",
            spend_guard=guard,
            max_call_usd=0.2,
            resilience=resilience,
        )

    assert guard._read().settled_usd == pytest.approx(0.2)

import pytest

from backend.core.model_router import (
    Tier,
    create_async_client,
    create_client,
    create_text_response,
    estimate_response_cost_usd,
    get_model,
)


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

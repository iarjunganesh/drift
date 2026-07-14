import pytest

from backend.agents.base import BaseAgent


class SuccessfulAgent(BaseAgent):
    async def run(self, input_data: str) -> str:
        return input_data.upper()


class FailingAgent(BaseAgent):
    async def run(self, input_data: str) -> str:
        raise RuntimeError(f"bad input: {input_data}")


@pytest.mark.asyncio
async def test_base_agent_logs_lifecycle_and_returns_result() -> None:
    assert await SuccessfulAgent("test")("ok") == "OK"


@pytest.mark.asyncio
async def test_base_agent_reraises_agent_error() -> None:
    with pytest.raises(RuntimeError, match="bad input: ok"):
        await FailingAgent("test")("ok")

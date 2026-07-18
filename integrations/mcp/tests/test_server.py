"""Tests for the three DRIFT MCP tools, exercised through FastMCP call_tool."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from integrations.mcp.client import DriftApiError
from integrations.mcp.server import build_server


class FakeClient:
    """Stand-in DriftApiClient with programmable responses per method."""

    def __init__(
        self,
        *,
        briefing: Any = None,
        search: Any = None,
        ask: Any = None,
        error: str | None = None,
    ) -> None:
        self._briefing = briefing
        self._search = search
        self._ask = ask
        self._error = error

    async def briefing(self, top_n: int) -> list[dict[str, Any]]:
        if self._error:
            raise DriftApiError(self._error)
        return self._briefing

    async def search(self, query: str) -> list[dict[str, Any]]:
        if self._error:
            raise DriftApiError(self._error)
        return self._search

    async def ask(self, question: str) -> dict[str, Any] | None:
        if self._error:
            raise DriftApiError(self._error)
        return self._ask


async def call_text(mcp: FastMCP, name: str, arguments: dict[str, Any]) -> str:
    blocks, _structured = await mcp.call_tool(name, arguments)
    return blocks[0].text


async def test_registers_exactly_three_named_tools() -> None:
    mcp = build_server(client=FakeClient())
    names = sorted(tool.name for tool in await mcp.list_tools())
    assert names == ["ask_drift", "drift_briefing", "drift_search"]


async def test_drift_briefing_returns_formatted_text() -> None:
    client = FakeClient(briefing=[{"rank": 1, "insight": {"title": "vLLM v0.25.1"}}])
    text = await call_text(build_server(client=client), "drift_briefing", {"top_n": 1})
    assert "DRIFT briefing" in text
    assert "vLLM v0.25.1" in text


async def test_drift_briefing_surfaces_api_error() -> None:
    client = FakeClient(error="Could not reach the DRIFT API at http://x.")
    text = await call_text(build_server(client=client), "drift_briefing", {})
    assert "Could not reach the DRIFT API" in text


async def test_drift_search_returns_formatted_text() -> None:
    client = FakeClient(search=[{"title": "NCCL v2.30.7-1"}])
    text = await call_text(build_server(client=client), "drift_search", {"query": "nccl"})
    assert "NCCL v2.30.7-1" in text


async def test_drift_search_surfaces_api_error() -> None:
    client = FakeClient(error="query must be between 2 and 300 characters.")
    text = await call_text(build_server(client=client), "drift_search", {"query": "x"})
    assert "query must be between" in text


async def test_ask_drift_returns_grounded_answer() -> None:
    client = FakeClient(
        ask={
            "answer": "vLLM changed scheduler defaults.",
            "source_citations": ["https://example.com/vllm"],
            "model_used": "gpt-5.6-terra",
            "grounded_insight_ids": [13],
        }
    )
    text = await call_text(build_server(client=client), "ask_drift", {"question": "vLLM?"})
    assert "vLLM changed scheduler defaults." in text
    assert "Answered by: gpt-5.6-terra" in text


async def test_ask_drift_declines_when_no_match() -> None:
    client = FakeClient(ask=None)
    text = await call_text(
        build_server(client=client), "ask_drift", {"question": "Tell me about PyTorch."}
    )
    assert "declines to answer" in text


async def test_ask_drift_surfaces_api_error() -> None:
    client = FakeClient(error="The DRIFT API returned HTTP 503 for POST /chat.")
    text = await call_text(build_server(client=client), "ask_drift", {"question": "vLLM?"})
    assert "HTTP 503" in text

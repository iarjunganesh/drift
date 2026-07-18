"""Mocked-HTTP tests for the thin DRIFT API client."""

import json

import httpx
import pytest
import respx

from integrations.mcp.client import DriftApiClient, DriftApiError

BASE_URL = "http://drift.test"


def make_client() -> DriftApiClient:
    return DriftApiClient(BASE_URL, timeout_seconds=5.0)


@respx.mock
async def test_briefing_calls_endpoint_with_top_n() -> None:
    route = respx.get(f"{BASE_URL}/briefing").mock(
        return_value=httpx.Response(200, json=[{"rank": 1, "insight": {"title": "x"}}])
    )
    result = await make_client().briefing(3)
    assert result == [{"rank": 1, "insight": {"title": "x"}}]
    assert route.calls.last.request.url.params["top_n"] == "3"


@pytest.mark.parametrize("top_n", [0, 11, -1])
async def test_briefing_rejects_out_of_range_top_n(top_n: int) -> None:
    with pytest.raises(DriftApiError, match="top_n"):
        await make_client().briefing(top_n)


@respx.mock
async def test_search_strips_query_and_returns_results() -> None:
    route = respx.get(f"{BASE_URL}/search").mock(
        return_value=httpx.Response(200, json=[{"title": "vLLM"}])
    )
    result = await make_client().search("  vllm  ")
    assert result == [{"title": "vLLM"}]
    assert route.calls.last.request.url.params["q"] == "vllm"


@pytest.mark.parametrize("query", ["", "a", " x "])
async def test_search_rejects_too_short_query(query: str) -> None:
    with pytest.raises(DriftApiError, match="query"):
        await make_client().search(query)


async def test_search_rejects_too_long_query() -> None:
    with pytest.raises(DriftApiError, match="query"):
        await make_client().search("q" * 301)


@respx.mock
async def test_ask_posts_question_and_returns_response() -> None:
    route = respx.post(f"{BASE_URL}/chat").mock(
        return_value=httpx.Response(200, json={"answer": "Yes", "source_citations": []})
    )
    result = await make_client().ask("What changed in vLLM?")
    assert result == {"answer": "Yes", "source_citations": []}
    assert json.loads(route.calls.last.request.content) == {"question": "What changed in vLLM?"}


@respx.mock
async def test_ask_returns_none_on_404() -> None:
    respx.post(f"{BASE_URL}/chat").mock(return_value=httpx.Response(404, json={"detail": "none"}))
    assert await make_client().ask("Anything about PyTorch?") is None


@pytest.mark.parametrize("question", ["", "ab", "q" * 2001])
async def test_ask_rejects_out_of_range_question(question: str) -> None:
    with pytest.raises(DriftApiError, match="question"):
        await make_client().ask(question)


@respx.mock
async def test_request_raises_on_server_error() -> None:
    respx.get(f"{BASE_URL}/briefing").mock(return_value=httpx.Response(503))
    with pytest.raises(DriftApiError, match="HTTP 503"):
        await make_client().briefing(5)


@respx.mock
async def test_request_raises_on_transport_error() -> None:
    respx.get(f"{BASE_URL}/briefing").mock(side_effect=httpx.ConnectError("refused"))
    with pytest.raises(DriftApiError, match="Could not reach the DRIFT API"):
        await make_client().briefing(5)

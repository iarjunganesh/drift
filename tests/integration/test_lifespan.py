from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.core.budget import SpendGuard
from backend.core.config import settings
from backend.core.store import InsightStore


@pytest.mark.asyncio
async def test_live_lifespan_initializes_a_model_client_and_spend_guard(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        replace(settings, mode="live", openai_api_key="test-key"),
    )

    class FakeClient:
        async def close(self) -> None:
            pass

    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async with main.lifespan(main.app):
        assert isinstance(main.app.state.openai_client, FakeClient)
        assert isinstance(main.app.state.spend_guard, main.SpendGuard)


@pytest.mark.asyncio
async def test_live_retrieval_helper_opens_a_session(monkeypatch) -> None:
    class SessionContext:
        async def __aenter__(self):
            return "session"

        async def __aexit__(self, *_args) -> None:
            pass

    async def fake_retrieval(session, query, *, client, limit):
        assert (session, query, client, limit) == ("session", "vllm", "client", 2)
        return []

    monkeypatch.setattr(main, "session_factory", lambda: SessionContext())
    monkeypatch.setattr(main, "retrieve_live_store_insights", fake_retrieval)
    main.app.state.openai_client = "client"

    assert await main._retrieve_live_insights("vllm", limit=2) == []


def test_live_chat_returns_the_live_model_audit_label(monkeypatch, tmp_path) -> None:
    class FakeResponses:
        async def create(self, **kwargs):
            assert kwargs["model"] == "gpt-5.6-terra"
            return type("Response", (), {"output_text": "Grounded response", "usage": None})()

    class FakeClient:
        responses = FakeResponses()

        async def close(self) -> None:
            pass

    monkeypatch.setattr(
        main,
        "settings",
        replace(
            settings,
            mode="live",
            openai_api_key="test-key",
            spend_ledger_path=str(tmp_path / "spend-ledger.json"),
        ),
    )
    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async def fixture_retrieval(query: str, *, limit: int = 5):
        return InsightStore.from_json(settings.fixture_path).search(query, limit=limit)

    monkeypatch.setattr(main, "_retrieve_live_insights", fixture_retrieval)

    with TestClient(main.app) as client:
        response = client.post("/chat", json={"question": "What should I check for vllm?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded response"
    assert response.json()["model_used"] == "gpt-5.6-terra"


@pytest.mark.parametrize(
    ("responses", "limit_usd", "expected_status"),
    [
        (None, 0.1, 429),
        (RuntimeError("provider unavailable"), 1, 502),
        (main.ModelCapacityExceededError("busy"), 1, 503),
        (main.ProviderCircuitOpenError("open"), 1, 503),
    ],
)
def test_live_chat_maps_budget_and_provider_failures(monkeypatch, tmp_path, responses, limit_usd, expected_status) -> None:
    class FakeResponses:
        async def create(self, **kwargs):
            if isinstance(responses, Exception):
                raise responses
            return type("Response", (), {"output_text": "Unused", "usage": None})()

    class FakeClient:
        responses = FakeResponses()

        async def close(self) -> None:
            pass

    monkeypatch.setattr(
        main,
        "settings",
        replace(
            settings,
            mode="live",
            openai_api_key="test-key",
            max_spend_usd=limit_usd,
            spend_alert_usd=limit_usd,
            max_call_usd=min(0.2, limit_usd),
            model_max_attempts=1,
            spend_ledger_path=str(tmp_path / "spend-ledger.json"),
        ),
    )
    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async def fixture_retrieval(query: str, *, limit: int = 5):
        return InsightStore.from_json(settings.fixture_path).search(query, limit=limit)

    monkeypatch.setattr(main, "_retrieve_live_insights", fixture_retrieval)
    ledger_path = tmp_path / "spend-ledger.json"
    if responses is None:
        SpendGuard(ledger_path, limit_usd=limit_usd, alert_usd=limit_usd).settle(
            0, 0.01, "prior-call"
        )

    with TestClient(main.app) as client:
        response = client.post("/chat", json={"question": "What should I check for vllm?"})

    assert response.status_code == expected_status


def test_live_search_uses_live_store(monkeypatch, tmp_path) -> None:
    class FakeClient:
        async def close(self) -> None:
            pass

    monkeypatch.setattr(
        main,
        "settings",
        replace(settings, mode="live", openai_api_key="test-key"),
    )
    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async def fixture_retrieval(query: str, *, limit: int = 5):
        return InsightStore.from_json(settings.fixture_path).search(query, limit=limit)

    monkeypatch.setattr(main, "_retrieve_live_insights", fixture_retrieval)

    with TestClient(main.app) as client:
        response = client.get("/search", params={"q": "vllm runtime"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == 1


def test_live_search_returns_service_unavailable_when_store_fails(monkeypatch) -> None:
    class FakeClient:
        async def close(self) -> None:
            pass

    monkeypatch.setattr(
        main,
        "settings",
        replace(settings, mode="live", openai_api_key="test-key"),
    )
    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async def failing_retrieval(_query: str, *, limit: int = 5):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(main, "_retrieve_live_insights", failing_retrieval)

    with TestClient(main.app) as client:
        response = client.get("/search", params={"q": "vllm runtime"})

    assert response.status_code == 503
    assert response.json()["detail"] == "The live Insight store could not be searched."


def test_live_chat_returns_service_unavailable_when_store_fails(monkeypatch) -> None:
    class FakeClient:
        async def close(self) -> None:
            pass

    monkeypatch.setattr(
        main,
        "settings",
        replace(settings, mode="live", openai_api_key="test-key"),
    )
    monkeypatch.setattr(main, "create_async_client", lambda *_: FakeClient())

    async def failing_retrieval(_query: str, *, limit: int = 5):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(main, "_retrieve_live_insights", failing_retrieval)

    with TestClient(main.app) as client:
        response = client.post("/chat", json={"question": "What should I check for vllm?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "The live Insight store could not be searched."

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.core.budget import SpendGuard
from backend.core.config import settings


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
    ledger_path = tmp_path / "spend-ledger.json"
    if responses is None:
        SpendGuard(ledger_path, limit_usd=limit_usd, alert_usd=limit_usd).settle(
            0, 0.01, "prior-call"
        )

    with TestClient(main.app) as client:
        response = client.post("/chat", json={"question": "What should I check for vllm?"})

    assert response.status_code == expected_status

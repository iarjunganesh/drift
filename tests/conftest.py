from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.core import model_router
from backend.core.config import settings


@pytest.fixture(autouse=True)
def isolate_model_spend_ledger(monkeypatch, tmp_path):
    """Prevent mocked provider tests from mutating the developer spend ledger."""
    monkeypatch.setattr(
        model_router,
        "settings",
        replace(
            settings,
            spend_ledger_path=str(tmp_path / "spend-ledger.json"),
            max_spend_usd=100,
            spend_alert_usd=50,
        ),
    )


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setattr(main, "settings", replace(settings, mode="fixture"))
    with TestClient(main.app) as client:
        yield client
